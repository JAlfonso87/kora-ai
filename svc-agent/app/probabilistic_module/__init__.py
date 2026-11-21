"""
Módulo de razonamiento probabilístico basado en el Teorema de Bayes.
Componente de Kora AI (HU-012) — especificación definitiva.
"""

from app.probabilistic_module.engine import BayesEngine, compute_posterior
from app.probabilistic_module.scenario_manager.scenario import (
    Hypothesis,
    Evidence,
    Scenario,
    ScenarioId,
    SCENARIOS,
    get_scenario,
    list_scenarios,
)
from app.probabilistic_module.result_manager.result_builder import BayesianResult

__all__ = [
    "BayesEngine",
    "compute_posterior",
    "Hypothesis",
    "Evidence",
    "Scenario",
    "ScenarioId",
    "SCENARIOS",
    "get_scenario",
    "list_scenarios",
    "BayesianResult",
]
