from agents.vendor_agents import Offer


def offer_score(offer: Offer, delivery_weight: float = 2.0) -> float:
    """Lower is better: total price plus a transparent delivery penalty."""
    return round(offer.total_price + offer.delivery_days * delivery_weight, 2)


def select_best_offer(offers: list[Offer], budget: float) -> Offer | None:
    eligible = [offer for offer in offers if offer.total_price <= budget]
    return min(eligible, key=offer_score, default=None)

