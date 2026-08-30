import os
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


class PaymentMismatchError(ValueError):
    pass


class PaymentConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class PaymentOrder:
    order_id: str
    amount_subunits: int
    currency: str
    receipt: str


def to_subunits(amount: float) -> int:
    return int((Decimal(str(amount)) * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class RazorpayPaymentClient:
    """Test-mode order creation. The client never accepts a client-supplied amount as authoritative."""

    def __init__(self, key_id: str | None = None, key_secret: str | None = None, client: Any | None = None):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "")
        self.client = client

    def _client(self) -> Any:
        if self.client is not None:
            return self.client
        if not self.key_id.startswith("rzp_test_") or not self.key_secret:
            raise PaymentConfigurationError("Razorpay Test Mode keys are not configured")
        import razorpay
        return razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_order(self, approved_offer: dict[str, Any], requested_amount: float, requested_currency: str, receipt: str) -> PaymentOrder:
        expected_amount = float(approved_offer["total_price"])
        expected_currency = str(approved_offer["currency"]).upper()
        if Decimal(str(requested_amount)) != Decimal(str(expected_amount)):
            raise PaymentMismatchError("payment amount does not match the approved offer")
        if requested_currency.upper() != expected_currency:
            raise PaymentMismatchError("payment currency does not match the approved offer")
        data = {"amount": to_subunits(expected_amount), "currency": expected_currency, "receipt": receipt[:40], "notes": {"vendor_id": str(approved_offer["vendor_id"]), "payment_mode": "test"}}
        try:
            response = self._client().order.create(data=data)
        except PaymentConfigurationError:
            raise
        except Exception as error:
            raise RuntimeError("Razorpay order creation failed") from error
        return PaymentOrder(str(response["id"]), int(response["amount"]), str(response["currency"]), str(response["receipt"]))
