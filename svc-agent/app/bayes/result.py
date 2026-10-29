
"""
HU-012-T04 — Resultado interpretable de Bayes.

Incluye:
- Posteriores normalizadas.
- Hipótesis dominante.
- Decisión sugerida.
- Nivel de confianza del modelo, no garantía de exactitud.
- Indicador de ambigüedad.
- Bloqueo de seguridad por reglas externas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isclose, isfinite
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.bayes.engine import BayesEngine


@dataclass
class HypothesisPosterior:
    id: str
    label: str
    probability: float
    prior: float


@dataclass
class BayesianResult:
    scenario_id: str
    scenario_name: str
    posteriors: List[HypothesisPosterior]
    most_probable_hypothesis: str
    most_probable_label: str
    most_probable_probability: float
    applied_evidence: List[str]
    decision: str
    confidence_level: str
    explanation: str
    ambiguous: bool = False
    safety_block: bool = False
    safety_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Devuelve una estructura compatible con JSON."""
        return {
            "success": True,
            "type": "bayes",
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "posteriors": [
                {
                    "id": posterior.id,
                    "label": posterior.label,
                    "probability": round(posterior.probability, 4),
                    "prior": round(posterior.prior, 4),
                }
                for posterior in self.posteriors
            ],
            "most_probable": {
                "hypothesis_id": self.most_probable_hypothesis,
                "label": self.most_probable_label,
                "probability": round(
                    self.most_probable_probability, 4
                ),
            },
            "applied_evidence": list(self.applied_evidence),
            "decision": self.decision,
            "confidence_level": self.confidence_level,
            "ambiguous": self.ambiguous,
            "safety_block": self.safety_block,
            "safety_reason": self.safety_reason,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }

    @classmethod
    def from_engine(
        cls,
        engine: "BayesEngine",
        *,
        safety_block: bool = False,
        safety_reason: Optional[str] = None,
    ) -> "BayesianResult":
        scenario = engine.scenario
        posterior_values = engine.posteriors

        total = sum(posterior_values.values())
        if (
            not isfinite(total)
            or total <= 0.0
            or not isclose(total, 1.0, abs_tol=1e-8)
        ):
            raise ValueError(
                f"Los posteriores deben sumar 1.0; suma recibida: {total}"
            )

        posteriors_list = [
            HypothesisPosterior(
                id=hypothesis.id,
                label=hypothesis.label,
                probability=posterior_values[hypothesis.id],
                prior=hypothesis.prior,
            )
            for hypothesis in scenario.hypotheses
        ]
        posteriors_list.sort(
            key=lambda posterior: posterior.probability,
            reverse=True,
        )

        top = posteriors_list[0]
        ambiguous = engine.is_ambiguous(margin=0.10)
        confidence = _confidence_level(
            top.probability,
            ambiguous,
        )

        if safety_block:
            decision = "blocked_by_safety"
            confidence = "low"
        else:
            decision = _make_decision(
                scenario.id.value,
                top.id,
                top.probability,
                ambiguous,
            )

        explanation = _build_explanation(
            scenario.name,
            top,
            engine.applied_evidence,
            confidence,
            ambiguous,
            safety_block,
            safety_reason,
        )

        return cls(
            scenario_id=scenario.id.value,
            scenario_name=scenario.name,
            posteriors=posteriors_list,
            most_probable_hypothesis=top.id,
            most_probable_label=top.label,
            most_probable_probability=top.probability,
            applied_evidence=engine.applied_evidence,
            decision=decision,
            confidence_level=confidence,
            ambiguous=ambiguous,
            safety_block=safety_block,
            safety_reason=safety_reason,
            explanation=explanation,
            metadata={
                "num_evidence_applied": len(engine.applied_evidence),
                "hypotheses_count": len(scenario.hypotheses),
                "posterior_sum": round(
                    sum(p.probability for p in posteriors_list), 10
                ),
                "conditional_independence_assumption": (
                    "Las evidencias se combinan secuencialmente suponiendo "
                    "independencia condicional dada cada hipótesis."
                ),
                "probability_status": (
                    "Priors y likelihoods definidos como supuestos del "
                    "modelo; requieren validación empírica."
                ),
                "note": (
                    "confidence_level y decision son interpretaciones "
                    "heurísticas del modelo; no garantizan exactitud real."
                ),
            },
        )


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
