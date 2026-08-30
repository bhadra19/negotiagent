from dataclasses import asdict
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agents.negotiation_agent import NegotiationAdvisor
from agents.vendor_agents import DEFAULT_VENDORS, Offer
from audit.logger import AuditLogger
from config import settings
from negotiation.engine import NegotiationEngine
from negotiation.substitution import find_substitutions
from payments.razorpay_client import PaymentConfigurationError, PaymentMismatchError, RazorpayPaymentClient
from security.policy_engine import PolicyEngine
from security.trust import VENDOR_TRUST_SCORES

app = FastAPI(title="NegotiAgent", version="0.1.0")
engine = NegotiationEngine(max_rounds=settings.max_rounds)
policy = PolicyEngine(set(DEFAULT_VENDORS), max_budget=1_000_000, max_rounds=settings.max_rounds, trust_scores=VENDOR_TRUST_SCORES)
audit = AuditLogger(settings.database_path)
advisor = NegotiationAdvisor(settings.openai_model)
payments = RazorpayPaymentClient()
if settings.openai_enabled:
    from openai import OpenAI
    advisor = NegotiationAdvisor(settings.openai_model, OpenAI())


class NegotiationRequest(BaseModel):
    item: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=10_000)
    budget: float = Field(gt=0)
    vendor_ids: list[str] | None = None


class SubstitutionRequest(BaseModel):
    item: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=10_000)
    budget: float = Field(gt=0)


class PaymentRequest(BaseModel):
    negotiation_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=8, max_length=128)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


def serialize_offer(offer: Offer) -> dict:
    return {**asdict(offer), "total_price": offer.total_price}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/negotiations")
def negotiate(request: NegotiationRequest) -> dict:
    negotiation_id = str(uuid4())
    try:
        result = engine.run(request.quantity, request.budget, request.vendor_ids)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    selected = result.selected_offer
    decision = policy.validate_offer(selected, request.budget, result.rounds_completed) if selected else None
    advisory = advisor.explain(request.item, request.budget, result.offers, selected)
    if selected and decision and decision.allowed:
        audit.save_approved_offer(negotiation_id, selected)
    audit.log(negotiation_id, "negotiation_completed", {"item": request.item, "quantity": request.quantity, "budget": request.budget, "rounds_completed": result.rounds_completed, "selected_vendor": selected.vendor_id if selected else None, "policy_allowed": decision.allowed if decision else False, "advisor_source": advisory.source})
    return {"negotiation_id": negotiation_id, "rounds_completed": result.rounds_completed, "offers": [serialize_offer(offer) for offer in result.offers], "selected_offer": serialize_offer(selected) if selected and decision and decision.allowed else None, "decision": decision.reason if decision else "no offer met the budget", "advisor": {"source": advisory.source, "rationale": advisory.text}}


@app.get("/negotiations/{negotiation_id}/audit")
def audit_events(negotiation_id: str) -> dict:
    return {"events": audit.list_events(negotiation_id)}


@app.post("/substitutions")
def substitutions(request: SubstitutionRequest) -> dict:
    options = find_substitutions(request.item, request.quantity, request.budget)
    return {"substitutions": [{"item": option.substitute_item, "unit_price": option.unit_price, "total_price": option.total_price(request.quantity), "delivery_days": option.delivery_days, "reason": option.reason} for option in options]}


@app.post("/payments/orders")
def create_payment_order(request: PaymentRequest) -> dict:
    approved_offer = audit.get_approved_offer(request.negotiation_id)
    if approved_offer is None:
        raise HTTPException(status_code=404, detail="no approved offer exists for this negotiation")
    attempt = audit.start_payment_attempt(request.negotiation_id, request.idempotency_key)
    if not attempt["created"]:
        if attempt["status"] == "created":
            return {"order_id": attempt["order_id"], "amount_subunits": attempt["amount_subunits"], "currency": attempt["currency"], "receipt": "replayed", "replayed": True}
        raise HTTPException(status_code=409, detail="payment attempt already failed; retry with a new idempotency key")
    try:
        receipt = "neg-" + request.negotiation_id.replace("-", "")[:24] + "-" + str(attempt["attempt_number"])
        order = payments.create_order(approved_offer, request.amount, request.currency, receipt)
    except PaymentMismatchError as error:
        audit.fail_payment_attempt(request.idempotency_key, "payment terms mismatch")
        raise HTTPException(status_code=400, detail=str(error)) from error
    except PaymentConfigurationError as error:
        audit.fail_payment_attempt(request.idempotency_key, "payment provider not configured")
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        audit.fail_payment_attempt(request.idempotency_key, "payment provider error")
        raise HTTPException(status_code=502, detail=str(error)) from error
    audit.complete_payment_attempt(request.idempotency_key, order.order_id, order.amount_subunits, order.currency)
    audit.log(request.negotiation_id, "payment_order_created", {"order_id": order.order_id, "amount_subunits": order.amount_subunits, "currency": order.currency})
    return {"order_id": order.order_id, "amount_subunits": order.amount_subunits, "currency": order.currency, "receipt": order.receipt, "replayed": False}


@app.get("/negotiations/{negotiation_id}/payment-attempts")
def payment_attempts(negotiation_id: str) -> dict:
    return {"attempts": audit.list_payment_attempts(negotiation_id)}
