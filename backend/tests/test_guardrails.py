from agents.vendor_agents import Offer
from security.policy_engine import PolicyEngine


def test_policy_rejects_unapproved_vendor():
    policy = PolicyEngine({"atlas-office"}, max_budget=1000)
    decision = policy.validate_offer(Offer("unknown", 10, 1, 1), 100, 3)
    assert not decision.allowed
    assert decision.reason == "vendor is not approved"


def test_policy_rejects_a_fourth_round():
    policy = PolicyEngine({"atlas-office"}, max_budget=1000)
    assert not policy.validate_offer(Offer("atlas-office", 10, 1, 1), 100, 4).allowed

