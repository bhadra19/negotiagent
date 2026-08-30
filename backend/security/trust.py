def trust_score(completed_orders: int, disputes: int, verified: bool) -> int:
    """Simple explainable 0-100 trust score for the prototype."""
    score = 50 + min(max(completed_orders, 0), 20) * 2 - min(max(disputes, 0), 10) * 8
    if verified:
        score += 10
    return max(0, min(100, score))

