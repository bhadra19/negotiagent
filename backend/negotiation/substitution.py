from dataclasses import dataclass


@dataclass(frozen=True)
class Substitution:
    requested_item: str
    substitute_item: str
    unit_price: float
    delivery_days: int
    reason: str

    def total_price(self, quantity: int) -> float:
        return round(self.unit_price * quantity, 2)


SUBSTITUTION_CATALOG = {
    "ergonomic chair": [
        Substitution("ergonomic chair", "mesh task chair", 85.0, 3, "Similar adjustable seating at a lower unit price."),
        Substitution("ergonomic chair", "lumbar support chair", 78.0, 2, "Lower-cost option with dedicated lumbar support."),
    ],
    "wireless keyboard": [
        Substitution("wireless keyboard", "compact wireless keyboard", 42.0, 2, "Compact layout with the same wireless use case."),
    ],
}


def find_substitutions(item: str, quantity: int, budget: float) -> list[Substitution]:
    if quantity < 1 or budget <= 0:
        raise ValueError("quantity and budget must be positive")
    normalized_item = item.strip().lower()
    return [option for option in SUBSTITUTION_CATALOG.get(normalized_item, []) if option.total_price(quantity) <= budget]
