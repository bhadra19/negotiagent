from dataclasses import dataclass
from agents.vendor_agents import DEFAULT_VENDORS, Offer, VendorSimulator
from negotiation.comparison import select_best_offer


@dataclass(frozen=True)
class NegotiationResult:
    offers: list[Offer]
    selected_offer: Offer | None
    rounds_completed: int


class NegotiationEngine:
    def __init__(self, vendors: dict[str, VendorSimulator] | None = None, max_rounds: int = 3):
        self.vendors = vendors or DEFAULT_VENDORS
        self.max_rounds = max_rounds

    def run(self, quantity: int, budget: float, vendor_ids: list[str] | None = None) -> NegotiationResult:
        if quantity < 1 or budget <= 0:
            raise ValueError("quantity and budget must be positive")
        selected_vendors = vendor_ids or list(self.vendors)
        unknown = set(selected_vendors) - set(self.vendors)
        if unknown:
            raise ValueError("unknown vendors: " + ", ".join(sorted(unknown)))
        offers = []
        for round_number in range(1, self.max_rounds + 1):
            for vendor_id in selected_vendors:
                offers.append(self.vendors[vendor_id].negotiate(quantity, round_number))
        return NegotiationResult(offers, select_best_offer(offers, budget), self.max_rounds)

