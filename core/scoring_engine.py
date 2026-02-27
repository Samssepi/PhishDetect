# core/scoring_engine.py


def aggregate(module_results: list):
    """
    Aggregates module signals into final risk intelligence output.
    Applies correlation and diversity-based amplification.
    """

    total_impact = 0
    triggered_categories = []
    indicators = []
    signal_count = 0

    for module in module_results:
        category = module.get("category")
        signals = module.get("signals", [])

        if signals:
            triggered_categories.append(category)

        for signal in signals:
            impact = signal.get("impact", 0)
            total_impact += impact
            signal_count += 1

            indicators.append({
                "title": signal.get("title"),
                "description": signal.get("description"),
                "category": category,
                "impact": impact
            })

    # --- Diversity Multiplier ---
    unique_categories = len(set(triggered_categories))

    diversity_multiplier = 1 + (0.15 * unique_categories)

    amplified_score = total_impact * diversity_multiplier

    # Clamp score
    risk_score = min(int(amplified_score), 100)

    # --- Severity Mapping ---
    if risk_score >= 80:
        severity = "Critical"
    elif risk_score >= 60:
        severity = "High"
    elif risk_score >= 30:
        severity = "Medium"
    else:
        severity = "Low"

    # --- Confidence Calculation ---
    # Based on diversity and signal volume
    confidence_base = (unique_categories * 20) + (signal_count * 5)
    confidence = min(confidence_base, 100)

    return {
        "risk_score": risk_score,
        "severity": severity,
        "confidence": confidence,
        "triggered_categories": list(set(triggered_categories)),
        "indicators": indicators
    }