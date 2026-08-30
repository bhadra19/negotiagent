from dataclasses import dataclass
from agents.vendor_agents import Offer


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self, approved_vendors: set[str], max_budget: float, max_rounds: int = 3):
        self.approved_vendors = approved_vendors
        self.max_budget = max_budget
        self.max_rounds = max_rounds

    def validate_offer(self, offer: Offer, requested_budget: float, rounds_completed: int) -> PolicyDecision:
        if offer.vendor_id not in self.approved_vendors:
            return PolicyDecision(False, "vendor is not approved")
        if rounds_completed > self.max_rounds:
            return PolicyDecision(False, "negotiation exceeded maximum rounds")
        if requested_budget > self.max_budget:
            return PolicyDecision(False, "requested budget exceeds policy limit")
        if offer.total_price > requested_budget:
            return PolicyDecision(False, "offer exceeds requested budget")
        return PolicyDecision(True, "offer meets deterministic policy")

