"""HU-012-T01: modelos y escenarios probabilísticos de Kora AI.

Los priors y likelihoods son supuestos iniciales para pruebas; no son
estimaciones validadas con datos reales. Deben evaluarse mediante pruebas
de sensibilidad y datos etiquetados (HU-012-T07).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Dict, List, Optional


class ScenarioId(str, Enum):
    MEAL_SUITABILITY = "meal_suitability"
    NUTRITIONAL_PRIORITY = "nutritional_priority"
    RECOMMENDATION_CONFIDENCE = "recommendation_confidence"


@dataclass(frozen=True)
class Hypothesis:
    id: str
    label: str
    prior: float

    def __post_init__(self) -> None:
        if not isfinite(self.prior) or not 0.0 < self.prior < 1.0:
            raise ValueError(f"Prior de '{self.id}' debe estar en (0, 1), recibido: {self.prior}")


@dataclass(frozen=True)
class Evidence:
    id: str
    label: str
    description: str = ""


@dataclass
class Scenario:
    id: ScenarioId
    name: str
    description: str
    hypotheses: List[Hypothesis]
    evidences: List[Evidence]
    # likelihoods[evidence_id][hypothesis_id] = P(E=true | H)
    likelihoods: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.hypotheses:
            raise ValueError(f"El escenario '{self.id.value}' necesita hipótesis.")
        hyp_ids = {h.id for h in self.hypotheses}
        evidence_ids = {e.id for e in self.evidences}
        if len(hyp_ids) != len(self.hypotheses):
            raise ValueError(f"Hay hipótesis duplicadas en '{self.id.value}'.")
        if len(evidence_ids) != len(self.evidences):
            raise ValueError(f"Hay evidencias duplicadas en '{self.id.value}'.")
        prior_sum = sum(h.prior for h in self.hypotheses)
        if abs(prior_sum - 1.0) > 1e-6:
            raise ValueError(f"Los priors de '{self.id.value}' deben sumar 1.0; suma: {prior_sum}")
        if set(self.likelihoods) != evidence_ids:
            missing = evidence_ids - set(self.likelihoods)
            extra = set(self.likelihoods) - evidence_ids
            raise ValueError(f"Likelihoods incompletos/extra en '{self.id.value}'. Faltan: {sorted(missing)}; sobran: {sorted(extra)}")
        for evidence_id, hyp_map in self.likelihoods.items():
            if set(hyp_map) != hyp_ids:
                missing = hyp_ids - set(hyp_map)
                extra = set(hyp_map) - hyp_ids
                raise ValueError(f"Likelihoods de '{evidence_id}' incompletos. Faltan: {sorted(missing)}; sobran: {sorted(extra)}")
            for hyp_id, likelihood in hyp_map.items():
                if not isfinite(likelihood) or not 0.0 <= likelihood <= 1.0:
                    raise ValueError(f"Likelihood P({evidence_id}|{hyp_id})={likelihood} fuera de [0,1].")

    def get_hypothesis(self, hyp_id: str) -> Optional[Hypothesis]:
        return next((h for h in self.hypotheses if h.id == hyp_id), None)

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return next((e for e in self.evidences if e.id == evidence_id), None)

    def likelihood(self, evidence_id: str, hypothesis_id: str) -> float:
        """Devuelve un likelihood configurado; nunca inventa un 0.5 por defecto."""
        try:
            return self.likelihoods[evidence_id][hypothesis_id]
        except KeyError as exc:
            raise KeyError(f"Likelihood no definido para '{evidence_id}' y '{hypothesis_id}'.") from exc


SCENARIOS: Dict[ScenarioId, Scenario] = {}


def _register(scenario: Scenario) -> Scenario:
    SCENARIOS[scenario.id] = scenario
    return scenario


_register(Scenario(
    id=ScenarioId.MEAL_SUITABILITY,
    name="Adecuación de comida",
    description=("Evalúa si una comida candidata es adecuada en el contexto actual. "
                 "Alergias y restricciones críticas se bloquean mediante reglas externas a Bayes."),
    hypotheses=[
        Hypothesis("suitable", "La comida cumple los criterios de recomendación", 0.50),
        Hypothesis("unsuitable", "La comida no cumple los criterios de recomendación", 0.50),
    ],
    evidences=[
        Evidence("macros_ok", "Macros alineados", "La comida se ajusta a los objetivos nutricionales disponibles."),
        Evidence("restrictions_ok", "Restricciones respetadas", "La comida respeta las restricciones conocidas."),
        Evidence("preferred_food", "Coincide con preferencias", "La comida coincide con preferencias conocidas."),
    ],
    likelihoods={
        "macros_ok": {"suitable": 0.80, "unsuitable": 0.30},
        "restrictions_ok": {"suitable": 0.95, "unsuitable": 0.10},
        "preferred_food": {"suitable": 0.65, "unsuitable": 0.45},
    },
))

_register(Scenario(
    id=ScenarioId.NUTRITIONAL_PRIORITY,
    name="Prioridad nutricional",
    description=("Estima qué enfoque conviene priorizar en la siguiente recomendación: proteína, "
                 "calorías o equilibrio. Es una señal de apoyo, no una indicación médica. "
                 "Los datos ausentes se omiten y no se interpretan como falsos."
                 "Las evidencias se combinan bajo un supuesto de independencia "
                "condicional dada cada hipótesis; este supuesto requiere validación."
                 ),
    hypotheses=[
        Hypothesis("protein_priority", "Priorizar una opción con proteína", 0.34),
        Hypothesis("calorie_priority", "Priorizar el objetivo de calorías", 0.33),
        Hypothesis("balanced_priority", "Mantener un enfoque equilibrado", 0.33),
    ],
    evidences=[
        Evidence("protein_below_target", "Proteína por debajo del objetivo", "Derivada de un objetivo válido y la ingesta/restante; no se combina con otra evidencia equivalente."),
        Evidence("calories_below_target", "Calorías por debajo del objetivo", "Derivada de un objetivo calórico válido y la ingesta/restante."),
        Evidence("balanced_goal", "Objetivo de alimentación equilibrada", "Señal explícita del objetivo principal de equilibrio."),
    ],
    likelihoods={
        "protein_below_target": {"protein_priority": 0.85, "calorie_priority": 0.35, "balanced_priority": 0.45},
        "calories_below_target": {"protein_priority": 0.35, "calorie_priority": 0.85, "balanced_priority": 0.45},
        "balanced_goal": {"protein_priority": 0.35, "calorie_priority": 0.35, "balanced_priority": 0.80},
    },
))

_register(Scenario(
    id=ScenarioId.RECOMMENDATION_CONFIDENCE,
    name="Respaldo de la recomendación",
    description=("Evalúa si la evidencia disponible respalda la recomendación. La confianza de visión "
                 "solo se considera cuando la imagen es relevante. Las reglas de seguridad bloquean "
                 "independientemente del posterior."),
    hypotheses=[
        Hypothesis("well_supported", "La recomendación tiene respaldo suficiente", 0.50),
        Hypothesis("insufficiently_supported", "La evidencia es insuficiente o contradictoria", 0.50),
    ],
    evidences=[
        Evidence("high_vision_confidence", "Alta confianza de visión", "La identificación visual supera el umbral cuando aplica."),
        Evidence("nutrition_data_available", "Datos nutricionales disponibles", "Están disponibles los datos nutricionales necesarios."),
        Evidence("context_complete", "Contexto completo", "Se dispone de los datos requeridos para esta decisión."),
        Evidence("evidence_consistent", "Evidencia consistente", "Las fuentes no presentan contradicciones relevantes."),
    ],
    likelihoods={
        "high_vision_confidence": {"well_supported": 0.80, "insufficiently_supported": 0.40},
        "nutrition_data_available": {"well_supported": 0.90, "insufficiently_supported": 0.30},
        "context_complete": {"well_supported": 0.85, "insufficiently_supported": 0.25},
        "evidence_consistent": {"well_supported": 0.85, "insufficiently_supported": 0.20},
    },
))


def get_scenario(scenario_id: str | ScenarioId) -> Scenario:
    if isinstance(scenario_id, str):
        try:
            scenario_id = ScenarioId(scenario_id)
        except ValueError as exc:
            raise KeyError(f"Escenario desconocido: {scenario_id}") from exc
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise KeyError(f"Escenario no registrado: {scenario_id}") from exc


def list_scenarios() -> List[dict]:
    return [{
        "id": scenario.id.value,
        "name": scenario.name,
        "description": scenario.description,
        "hypotheses": [{"id": h.id, "label": h.label, "prior": h.prior} for h in scenario.hypotheses],
        "evidences": [{"id": e.id, "label": e.label, "description": e.description} for e in scenario.evidences],
    } for scenario in SCENARIOS.values()]
