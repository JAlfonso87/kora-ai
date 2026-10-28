
"""
HU-012-T02 — Cálculo de probabilidad posterior mediante Bayes.

P(H | E) = P(E | H) * P(H) / P(E)

P(E) se calcula con la ley de probabilidad total.
La ausencia de evidencia utiliza 1 - P(E | H).

Las evidencias se actualizan secuencialmente bajo el supuesto de
independencia condicional entre evidencias dada cada hipótesis.
"""

from __future__ import annotations

from math import isclose, isfinite
from typing import Dict, List, Sequence

from app.bayes.models import Scenario, get_scenario
from app.bayes.result import BayesianResult


class BayesEngine:
    """Motor de inferencia bayesiana con posteriores normalizadas."""

    def __init__(self, scenario: Scenario | str):
        if isinstance(scenario, str):
            scenario = get_scenario(scenario)

        self.scenario: Scenario = scenario
        self._posteriors: Dict[str, float] = {
            hypothesis.id: hypothesis.prior
            for hypothesis in scenario.hypotheses
        }
        self._applied_evidence: List[str] = []

    @property
    def posteriors(self) -> Dict[str, float]:
        return dict(self._posteriors)

    @property
    def applied_evidence(self) -> List[str]:
        return list(self._applied_evidence)

    def reset(self) -> None:
        """Restablece las probabilidades previas del escenario."""
        self._posteriors = {
            hypothesis.id: hypothesis.prior
            for hypothesis in self.scenario.hypotheses
        }
        self._applied_evidence = []

    def update(
        self,
        evidence_id: str,
        present: bool = True,
    ) -> Dict[str, float]:
        """Actualiza los posteriores usando una evidencia."""

        if type(present) is not bool:
            raise TypeError("present debe ser bool.")

        evidence_definition = self.scenario.get_evidence(evidence_id)
        if evidence_definition is None:
            raise KeyError(
                f"Evidencia '{evidence_id}' no definida en el escenario "
                f"'{self.scenario.id.value}'."
            )

        # No permitir que una misma evidencia se contabilice dos veces.
        already_applied = any(
            marker.removeprefix("¬") == evidence_id
            for marker in self._applied_evidence
        )
        if already_applied:
            raise ValueError(
                f"La evidencia '{evidence_id}' ya fue aplicada. "
                "Restablece el motor antes de volver a calcular."
            )

        # P(E | H), o P(no E | H) si la evidencia está ausente.
        likelihoods: Dict[str, float] = {}

        for hypothesis in self.scenario.hypotheses:
            probability = self.scenario.likelihood(
                evidence_id,
                hypothesis.id,
            )

            likelihoods[hypothesis.id] = (
                probability if present else 1.0 - probability
            )

        # P(E) = sum(P(E | H) * P(H)).
        evidence_probability = sum(
            likelihoods[hypothesis_id] * posterior
            for hypothesis_id, posterior in self._posteriors.items()
        )

        if (
            not isfinite(evidence_probability)
            or evidence_probability <= 1e-12
        ):
            raise ValueError(
                f"La evidencia '{evidence_id}' tiene una probabilidad "
                "marginal nula o demasiado pequeña bajo el modelo."
            )

        new_posteriors = {
            hypothesis_id: (
                likelihoods[hypothesis_id] * posterior
            ) / evidence_probability
            for hypothesis_id, posterior in self._posteriors.items()
        }

        # Comprobar y normalizar la distribución posterior.
        total = sum(new_posteriors.values())

        if (
            not isfinite(total)
            or total <= 0.0
            or any(
                not isfinite(probability) or probability < 0.0
                for probability in new_posteriors.values()
            )
        ):
            raise ArithmeticError(
                "El cálculo produjo probabilidades posteriores inválidas."
            )

        self._posteriors = {
            hypothesis_id: probability / total
            for hypothesis_id, probability in new_posteriors.items()
        }

        marker = evidence_id if present else f"¬{evidence_id}"
        self._applied_evidence.append(marker)

        return self.posteriors

    def update_many(
        self,
        evidence_ids: Sequence[str],
        present: bool = True,
    ) -> Dict[str, float]:
        """Aplica una secuencia de evidencias no repetidas."""
        if type(present) is not bool:
            raise TypeError("present debe ser bool.")

        for evidence_id in evidence_ids:
            self.update(evidence_id, present=present)

        return self.posteriors

    def most_probable(self) -> tuple[str, float]:
        hypothesis_id = max(
            self._posteriors,
            key=self._posteriors.get,
        )
        return hypothesis_id, self._posteriors[hypothesis_id]

    def is_ambiguous(self, margin: float = 0.10) -> bool:
        """Indica si las dos hipótesis principales están muy próximas."""
        if not 0.0 <= margin <= 1.0:
            raise ValueError("margin debe estar entre 0 y 1.")

        ordered = sorted(
            self._posteriors.values(),
            reverse=True,
        )

        if len(ordered) < 2:
            return False

        return (ordered[0] - ordered[1]) < margin

    def to_result(self) -> BayesianResult:
        return BayesianResult.from_engine(self)


def compute_posterior(
    scenario_id: str,
    evidence: List[str] | Dict[str, bool],
) -> BayesianResult:
    """Calcula el posterior de un escenario desde sus priors."""

    engine = BayesEngine(scenario_id)

    if isinstance(evidence, dict):
        for evidence_id, present in evidence.items():
            engine.update(evidence_id, present=present)
    elif isinstance(evidence, list):
        engine.update_many(evidence)
    else:
        raise TypeError("evidence debe ser una lista o un diccionario.")

    return engine.to_result()
