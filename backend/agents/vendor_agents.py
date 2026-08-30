from dataclasses import dataclass


@dataclass(frozen=True)
class Offer:
    vendor_id: str
    unit_price: float
    quantity: int
    delivery_days: int
    currency: str = "INR"

    @property
    def total_price(self) -> float:
        return round(self.unit_price * self.quantity, 2)


@dataclass(frozen=True)
class VendorProfile:
    vendor_id: str
    starting_price: float
    floor_price: float
    delivery_days: int
    concession_per_round: float


class VendorSimulator:
    """Deterministic counterparty used until real vendor integrations are added."""

    def __init__(self, profile: VendorProfile):
        self.profile = profile

    def negotiate(self, quantity: int, round_number: int) -> Offer:
        if round_number < 1:
            raise ValueError("round_number must be at least 1")
        price = max(self.profile.floor_price, self.profile.starting_price - self.profile.concession_per_round * (round_number - 1))
        return Offer(self.profile.vendor_id, round(price, 2), quantity, self.profile.delivery_days)


DEFAULT_VENDORS = {
    "atlas-office": VendorSimulator(VendorProfile("atlas-office", 110.0, 96.0, 4, 7.0)),
    "banyan-supply": VendorSimulator(VendorProfile("banyan-supply", 106.0, 98.0, 2, 4.0)),
    "cobalt-traders": VendorSimulator(VendorProfile("cobalt-traders", 118.0, 92.0, 7, 13.0)),
}

