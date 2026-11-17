
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

from app.probabilistic_module.result_manager.explanation_builder import _build_explanation
from app.probabilistic_module.result_manager.deliberator import _confidence_level, _make_decision
from app.probabilistic_module.models import HypothesisPosterior

if TYPE_CHECKING:
    from app.probabilistic_module.engine import BayesEngine

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