"""
HU-012-T05 — Exponer el módulo como tool.

bayes_tool es la interfaz para LangGraph / LangChain y para el endpoint REST.
Las reglas de seguridad (alergias, restricciones críticas) se evalúan
ANTES de devolver la decisión final y pueden forzar safety_block.
"""
from __future__ import annotations

from app.toolbox_module.general_tools.models.input_models_general import BayesReasoningRequirements
from app.context_module.nutritional_profile.models import NutritionalContext

from typing import Any, Dict, List, Optional, Union

from app.probabilistic_module.engine import BayesEngine
from app.probabilistic_module.evidence import EvidenceProcessor
from app.probabilistic_module.scenario_manager.scenario import list_scenarios, get_scenario
from app.probabilistic_module.result_manager.result_builder import BayesianResult

from pydantic import BaseModel

class BayesTool:
    def bayes_reasoning_query(
        self,
        context: NutritionalContext | None,
        params: BayesReasoningRequirements,
        ) -> dict[str, Any]:
        """Run HU-012 Bayesian reasoning inside svc-agente (not a microservice)."""
        print("<< TOOL: bayes_reasoning >>")
        current_context = context or NutritionalContext()

        if hasattr(current_context, "model_dump"):
            context_data = current_context.model_dump(mode="python", exclude_none=True)
        elif hasattr(current_context, "dict"):
            context_data = current_context.dict(exclude_none=True)
        else:
            context_data = {}

        # Merge only the optional, scenario-specific signals supplied to the tool.
        # These must be grounded in the request/history/context, not guessed.
        if params.context:
            context_data.update(params.context)

        result = self.bayes_tool(
            scenario_id=params.scenario_id,
            evidence=params.evidence,
            context=context_data,
        )
        return {"content": result, "context": current_context}

    def bayes_tool(
        self,
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
        evidence = self._normalize_evidence(evidence)
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
                        self._raise_invalid_evidence(key)
                    )

            elif isinstance(evidence, list):
                for key, value in processor.from_list(evidence).items():
                    evidence_map.setdefault(key, value)
            else:
                raise TypeError(
                    "evidence debe ser una lista de IDs o un mapa de booleanos."
                )

        safety_block, safety_reason = self._check_safety(context)

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

    def _normalize_evidence(self, evidence: Any) -> Any:
        """Convierte modelos Pydantic a estructuras Python."""
        if isinstance(evidence, BaseModel):
            return evidence.model_dump(exclude_none=True)

        return evidence

    def _raise_invalid_evidence(self, key: str) -> bool:
        raise TypeError(
            f"La evidencia '{key}' debe ser bool; "
            "no se aceptan valores distintos de True o False."
        )


    def _check_safety(self, context: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
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

    def list_bayes_scenarios() -> Dict[str, Any]:
        return {
            "success": True,
            "type": "bayes_scenarios",
            "scenarios": list_scenarios(),
        }