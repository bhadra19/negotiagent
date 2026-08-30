def trust_score(completed_orders: int, disputes: int, verified: bool) -> int:
    """Simple explainable 0-100 trust score for the prototype."""
    score = 50 + min(max(completed_orders, 0), 20) * 2 - min(max(disputes, 0), 10) * 8
    if verified:
        score += 10
    return max(0, min(100, score))


VENDOR_TRUST_SCORES = {
    "atlas-office": trust_score(12, 0, True),
    "banyan-supply": trust_score(7, 0, True),
    "cobalt-traders": trust_score(17, 1, True),
}
