import pytest

from payments.razorpay_client import PaymentMismatchError, RazorpayPaymentClient


class FakeOrderAPI:
    def __init__(self):
        self.data = None

    def create(self, data):
        self.data = data
        return {"id": "order_test_123", "amount": data["amount"], "currency": data["currency"], "receipt": data["receipt"]}


class FakeClient:
    def __init__(self):
        self.order = FakeOrderAPI()


def approved_offer():
    return {"vendor_id": "cobalt-traders", "total_price": 184.0, "currency": "INR"}


def test_payment_order_uses_approved_amount_in_subunits():
    client = FakeClient()
    order = RazorpayPaymentClient(client=client).create_order(approved_offer(), 184.0, "INR", "neg-1")
    assert order.order_id == "order_test_123"
    assert client.order.data["amount"] == 18400
    assert client.order.data["currency"] == "INR"


def test_payment_rejects_amount_mismatch_before_provider_call():
    client = FakeClient()
    with pytest.raises(PaymentMismatchError, match="amount"):
        RazorpayPaymentClient(client=client).create_order(approved_offer(), 183.0, "INR", "neg-1")
    assert client.order.data is None


def test_payment_rejects_currency_mismatch_before_provider_call():
    with pytest.raises(PaymentMismatchError, match="currency"):
        RazorpayPaymentClient(client=FakeClient()).create_order(approved_offer(), 184.0, "USD", "neg-1")
