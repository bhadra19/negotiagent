from negotiation.engine import NegotiationEngine


def test_negotiation_runs_exactly_three_rounds_and_selects_offer():
    result = NegotiationEngine().run(quantity=2, budget=210)
    assert result.rounds_completed == 3
    assert len(result.offers) == 9
    assert result.selected_offer is not None
    assert result.selected_offer.vendor_id == "cobalt-traders"
    assert result.selected_offer.total_price == 184


def test_negotiation_returns_no_offer_when_budget_is_too_low():
    assert NegotiationEngine().run(quantity=1, budget=50).selected_offer is None

