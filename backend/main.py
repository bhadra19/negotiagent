from dataclasses import asdict
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agents.negotiation_agent import NegotiationAdvisor
from agents.vendor_agents import DEFAULT_VENDORS, Offer
from audit.logger import AuditLogger
from config import settings
from negotiation.engine import NegotiationEngine
from security.policy_engine import PolicyEngine

app = FastAPI(title="NegotiAgent", version="0.1.0")
engine = NegotiationEngine(max_rounds=settings.max_rounds)
policy = PolicyEngine(set(DEFAULT_VENDORS), max_budget=1_000_000, max_rounds=settings.max_rounds)
audit = AuditLogger(settings.database_path)
advisor = NegotiationAdvisor(settings.openai_model)
if settings.openai_enabled:
    from openai import OpenAI
    advisor = NegotiationAdvisor(settings.openai_model, OpenAI())


class NegotiationRequest(BaseModel):
    item: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=10_000)
    budget: float = Field(gt=0)
    vendor_ids: list[str] | None = None


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
    audit.log(negotiation_id, "negotiation_completed", {"item": request.item, "quantity": request.quantity, "budget": request.budget, "rounds_completed": result.rounds_completed, "selected_vendor": selected.vendor_id if selected else None, "policy_allowed": decision.allowed if decision else False, "advisor_source": advisory.source})
    return {"negotiation_id": negotiation_id, "rounds_completed": result.rounds_completed, "offers": [serialize_offer(offer) for offer in result.offers], "selected_offer": serialize_offer(selected) if selected and decision and decision.allowed else None, "decision": decision.reason if decision else "no offer met the budget", "advisor": {"source": advisory.source, "rationale": advisory.text}}


@app.get("/negotiations/{negotiation_id}/audit")
def audit_events(negotiation_id: str) -> dict:
    return {"events": audit.list_events(negotiation_id)}
