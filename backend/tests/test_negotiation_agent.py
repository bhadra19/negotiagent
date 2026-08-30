from types import SimpleNamespace

from agents.negotiation_agent import NegotiationAdvisor
from agents.vendor_agents import Offer


class FakeResponses:
    def __init__(self):
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_text="The selected offer is under budget and balances delivery time.")


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_advisor_only_explains_the_deterministic_selection():
    client = FakeClient()
    selected = Offer("atlas-office", 96, 1, 4)
    result = NegotiationAdvisor("test-model", client).explain("chair", 100, [selected], selected)

    assert result.source == "openai"
    assert "deterministic comparison" in client.responses.request["input"]
    assert client.responses.request["store"] is False
    assert "must not claim authority" in client.responses.request["instructions"]


def test_advisor_uses_safe_fallback_without_client():
    result = NegotiationAdvisor("test-model").explain("chair", 100, [], None)
    assert result.source == "fallback"


def test_advisor_failure_does_not_block_the_deterministic_flow():
    class FailingResponses:
        def create(self, **kwargs):
            raise RuntimeError("provider unavailable")

    result = NegotiationAdvisor("test-model", SimpleNamespace(responses=FailingResponses())).explain("chair", 100, [], None)
    assert result.source == "fallback"
