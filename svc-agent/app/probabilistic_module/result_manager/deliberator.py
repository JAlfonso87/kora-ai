def _confidence_level(
    probability: float,
    ambiguous: bool,
) -> str:
    if ambiguous:
        return "low"
    if probability >= 0.75:
        return "high"
    if probability >= 0.55:
        return "medium"
    return "low"


def _make_decision(
    scenario_id: str,
    hyp_id: str,
    prob: float,
    ambiguous: bool,
) -> str:
    if scenario_id == "meal_suitability":
        if hyp_id == "suitable" and prob >= 0.65 and not ambiguous:
            return "recommend"
        if hyp_id == "suitable" and prob >= 0.45:
            return "recommend_with_caution"
        return "do_not_recommend"

    if scenario_id == "nutritional_priority":
        if ambiguous:
            return "request_more_context"
        if hyp_id == "protein_priority" and prob >= 0.60:
            return "prioritize_protein"
        if hyp_id == "calorie_priority" and prob >= 0.60:
            return "prioritize_calories"
        if hyp_id == "balanced_priority" and prob >= 0.50:
            return "maintain_balance"
        return "request_more_context"

    if scenario_id == "recommendation_confidence":
        if hyp_id == "well_supported" and prob >= 0.70 and not ambiguous:
            return "accept_recommendation"
        if hyp_id == "well_supported":
            return "accept_with_review"
        return "request_more_context"

    return f"select_{hyp_id}"