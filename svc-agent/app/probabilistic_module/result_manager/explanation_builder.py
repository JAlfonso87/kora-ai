from typing import List, Optional
from app.probabilistic_module.models import HypothesisPosterior

def _build_explanation(
    scenario_name: str,
    top: HypothesisPosterior,
    applied: List[str],
    confidence: str,
    ambiguous: bool,
    safety_block: bool,
    safety_reason: Optional[str],
) -> str:
    evidence_text = (
        ", ".join(applied)
        if applied
        else "ninguna evidencia adicional"
    )

    parts = [
        f"Escenario '{scenario_name}'.",
        f"Evidencias consideradas: [{evidence_text}].",
        (
            f"Hipótesis más probable: '{top.label}' "
            f"({top.probability:.2%})."
        ),
        f"Probabilidad previa de esa hipótesis: {top.prior:.2%}.",
        f"Confianza interpretativa del modelo: {confidence}.",
    ]

    if ambiguous:
        parts.append(
            "Las dos hipótesis principales están próximas. "
            "El resultado es ambiguo y no debe tratarse como certeza."
        )

    if safety_block:
        parts.append(
            "BLOQUEO DE SEGURIDAD: "
            f"{safety_reason or 'restricción crítica detectada'}."
        )

    parts.append(
        "Los posteriores dependen de los priors y likelihoods configurados. "
        "Estos parámetros no están validados con datos reales y las "
        "evidencias se combinan bajo un supuesto de independencia "
        "condicional."
    )

    return " ".join(parts)
