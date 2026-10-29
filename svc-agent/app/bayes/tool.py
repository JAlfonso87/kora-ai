"""
HU-012-T05 — Exponer el módulo como tool.

bayes_tool es la interfaz para LangGraph / LangChain y para el endpoint REST.
Las reglas de seguridad (alergias, restricciones críticas) se evalúan
ANTES de devolver la decisión final y pueden forzar safety_block.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from app.bayes.engine import BayesEngine, compute_posterior
from app.bayes.evidence import EvidenceProcessor
from app.bayes.models import list_scenarios, get_scenario, ScenarioId
from app.bayes.result import BayesianResult
from pydantic import BaseModel
def _normalize_evidence(evidence: Any) -> Any:
    """Convierte modelos Pydantic a estructuras Python."""
    if isinstance(evidence, BaseModel):
        return evidence.model_dump(exclude_none=True)

    return evidence

def _raise_invalid_evidence(key: str) -> bool:
    raise TypeError(
        f"La evidencia '{key}' debe ser bool; "
        "no se aceptan valores distintos de True o False."
    )


def _check_safety(context: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """
    Reglas fuera de Bayes. Si retorna (True, reason), la decisión se bloquea
    independientemente del posterior.
    """
    if not context:
        return False, None

    if context.get("critical_allergy") is True:
        return True, "Alergia conocida / incompatibilidad crítica confirmada"

    if context.get("unavailable") is True:
        return True, "Alimento no disponible; verificar disponibilidad antes de recomendar"

    # Lista explícita de alérgenos en la comida candidata
    allergies = context.get("allergies") or []
    candidate_foods = context.get("candidate_foods") or context.get("foods") or []
    if allergies and candidate_foods:
        allergy_set = {a.lower() for a in allergies}
        for food in candidate_foods:
            if str(food).lower() in allergy_set:
                return True, f"Alimento '{food}' está en la lista de alergias del usuario"

    return False, None


def bayes_tool(
    scenario_id: str,
    evidence: Optional[Union[List[str], Dict[str, bool]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Tool de razonamiento probabilístico.

    Las evidencias derivables se obtienen del contexto.
    Los identificadores desconocidos se rechazan.
    """
    try:
        scenario = get_scenario(scenario_id)
    except KeyError as exc:
        return {
            "success": False,
            "type": "bayes",
            "error": str(exc),
            "available_scenarios": [s["id"] for s in list_scenarios()],
        }

    processor = EvidenceProcessor(scenario)
    context = context or {}
    evidence = _normalize_evidence(evidence)
    # Primero se derivan las evidencias desde los datos disponibles.
    evidence_map: Dict[str, bool] = processor.from_context(context)

    # Se aceptan evidencias explícitas únicamente si son válidas.
    if evidence is not None:
        if isinstance(evidence, dict):
            unknown = set(evidence) - processor._valid_ids

            if unknown:
                # En nutritional_priority, las señales derivadas
                # se calculan desde el contexto, no desde el LLM.
                derived_ids = {
                    "protein_below_target",
                    "calories_below_target",
                }

                if (
                    scenario.id.value == "nutritional_priority"
                    and unknown.issubset(derived_ids)
                ):
                    evidence = {
                        key: value
                        for key, value in evidence.items()
                        if key not in unknown
                    }
                else:
                    raise ValueError(
                        f"Evidencias no válidas para "
                        f"'{scenario.id.value}': {sorted(unknown)}"
                    )

            # El contexto tiene prioridad para las señales derivadas.
            # No se duplican ni se sobrescriben con señales del modelo.
            for key, value in evidence.items():
                if (
                    scenario.id.value == "nutritional_priority"
                    and key in {
                        "protein_below_target",
                        "calories_below_target",
                    }
                    and key in evidence_map
                ):
                    continue

                evidence_map[key] = value if type(value) is bool else (
                    _raise_invalid_evidence(key)
                )

        elif isinstance(evidence, list):
            for key, value in processor.from_list(evidence).items():
                evidence_map.setdefault(key, value)
        else:
            raise TypeError(
                "evidence debe ser una lista de IDs o un mapa de booleanos."
            )

    safety_block, safety_reason = _check_safety(context)

    engine = BayesEngine(scenario)

    for evidence_id, present in evidence_map.items():
        engine.update(evidence_id, present=present)

    result = BayesianResult.from_engine(
        engine,
        safety_block=safety_block,
        safety_reason=safety_reason,
    )

    if not evidence_map and not safety_block:
        result.explanation = (
            "No se proporcionó evidencia suficiente; se reportan "
            "las probabilidades a priori. " + result.explanation
        )

    return result.to_dict()


def list_bayes_scenarios() -> Dict[str, Any]:
    return {
        "success": True,
        "type": "bayes_scenarios",
        "scenarios": list_scenarios(),
    }


BAYES_TOOL_SCHEMA = {
    "name": "bayes_reasoning",
    "description": (
        "Aplica razonamiento probabilístico (Teorema de Bayes) para manejar "
        "incertidumbre en decisiones del agente de nutrición. "
        "Escenarios activos: meal_suitability, nutritional_priority y "
        "recommendation_confidence. Las restricciones críticas bloquean fuera de Bayes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "scenario_id": {
                "type": "string",
                "enum": [s.value for s in ScenarioId],
                "description": "Escenario de razonamiento a utilizar.",
            },
            
        "evidence": {
            "type": "object",
            "description": (
                "Mapa opcional de evidencias booleanas registradas para el escenario. "
                "No inventes identificadores. En nutritional_priority, "
                "protein_below_target y calories_below_target se derivan del contexto "
                "nutricional cuando hay datos suficientes."
            ),
        },
        "context": {
            "type": "object",
            "description": (
                "Contexto nutricional del usuario. Puede contener campos anidados "
                "como goals, current_consumption y remaining_nutrients, además de "
                "macros_ok, restrictions_ok, preferred_food, balanced_goal, "
                "primary_goal, vision_confidence, critical_allergy, allergies "
                "y candidate_foods. Usa únicamente datos disponibles y no inventes "
                "evidencias."
            ),
        },

        },
        "required": ["scenario_id"],
    },
}
