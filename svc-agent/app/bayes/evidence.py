
"""HU-012-T03: procesa señales del contexto como evidencias no duplicadas."""

from __future__ import annotations

from math import isfinite
from typing import Any, Dict, List, Sequence, Union

from app.bayes.models import Scenario, get_scenario


def _strict_bool(value: Any, *, field: str) -> bool:
    if type(value) is not bool:
        raise TypeError(
            f"La evidencia '{field}' debe ser bool; "
            f"recibido {type(value).__name__}."
        )
    return value


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if isfinite(number) else None


class EvidenceProcessor:
    def __init__(self, scenario: Scenario | str):
        self.scenario = (
            get_scenario(scenario) if isinstance(scenario, str) else scenario
        )
        self._valid_ids = {e.id for e in self.scenario.evidences}

    def validate(self, evidence_ids: Sequence[str]) -> List[str]:
        unknown = set(evidence_ids) - self._valid_ids

        if unknown:
            raise ValueError(
                f"Evidencias no válidas para '{self.scenario.id.value}': "
                f"{sorted(unknown)}"
            )

        return list(dict.fromkeys(evidence_ids))

    def from_list(
        self,
        evidence_ids: Sequence[str],
        *,
        present: bool = True,
    ) -> Dict[str, bool]:
        _strict_bool(present, field="present")
        return {
            evidence_id: present
            for evidence_id in self.validate(evidence_ids)
        }

    def from_context(self, context: Dict[str, Any]) -> Dict[str, bool]:
        if not isinstance(context, dict):
            raise TypeError("context debe ser un diccionario.")

        mapper = _CONTEXT_MAPPERS[self.scenario.id.value]
        return mapper(context, self._valid_ids)

    def merge(
        self,
        *sources: Union[Dict[str, bool], Sequence[str]],
    ) -> Dict[str, bool]:
        result: Dict[str, bool] = {}

        for source in sources:
            if isinstance(source, dict):
                unknown = set(source) - self._valid_ids

                if unknown:
                    raise ValueError(
                        f"Evidencias no válidas para "
                        f"'{self.scenario.id.value}': {sorted(unknown)}"
                    )

                for key, value in source.items():
                    result[key] = _strict_bool(value, field=key)
            else:
                result.update(self.from_list(source))

        return result


def _copy_bool(
    ctx: Dict[str, Any],
    out: Dict[str, bool],
    valid: set,
    key: str,
) -> None:
    if key in valid and key in ctx:
        out[key] = _strict_bool(ctx[key], field=key)


def _map_meal_suitability(
    ctx: Dict[str, Any],
    valid: set,
) -> Dict[str, bool]:
    out: Dict[str, bool] = {}

    _copy_bool(ctx, out, valid, "macros_ok")

    if "restrictions_ok" in valid:
        if ctx.get("critical_allergy") is True:
            out["restrictions_ok"] = False
        elif "restrictions_ok" in ctx:
            out["restrictions_ok"] = _strict_bool(
                ctx["restrictions_ok"],
                field="restrictions_ok",
            )

    _copy_bool(ctx, out, valid, "preferred_food")
    return out


def _goal_value(ctx: Dict[str, Any], key: str) -> Any:
    goals = ctx.get("goals")

    if ctx.get(key) is not None:
        return ctx[key]

    if isinstance(goals, dict):
        return goals.get(key)

    return None


def _map_nutritional_priority(
    ctx: Dict[str, Any],
    valid: set,
) -> Dict[str, bool]:
    out: Dict[str, bool] = {}

    remaining_nutrients = ctx.get("remaining_nutrients")
    current_consumption = ctx.get("current_consumption")

    if not isinstance(remaining_nutrients, dict):
        remaining_nutrients = {}

    if not isinstance(current_consumption, dict):
        current_consumption = {}

    # Proteína: usar una señal explícita si existe; de lo contrario,
    # derivarla de los datos numéricos disponibles.
    if "protein_below_target" in valid:
        if "protein_below_target" in ctx:
            out["protein_below_target"] = _strict_bool(
                ctx["protein_below_target"],
                field="protein_below_target",
            )
        else:
            target = _number(_goal_value(ctx, "protein_target_g"))
            remaining = _number(
                ctx.get("protein_remaining_g")
                if ctx.get("protein_remaining_g") is not None
                else remaining_nutrients.get("protein_g")
            )
            consumed = _number(
                ctx.get("protein_consumed_g")
                if ctx.get("protein_consumed_g") is not None
                else current_consumption.get("protein_g")
            )

            if target is not None and target > 0:
                if remaining is not None:
                    out["protein_below_target"] = remaining > 0
                elif consumed is not None:
                    out["protein_below_target"] = consumed < target

    # Calorías: la señal se deriva de la meta, el consumo o las
    # calorías restantes. Los datos desconocidos se omiten.
    if "calories_below_target" in valid:
        if "calories_below_target" in ctx:
            out["calories_below_target"] = _strict_bool(
                ctx["calories_below_target"],
                field="calories_below_target",
            )
        else:
            target = _number(_goal_value(ctx, "calorie_target_kcal"))
            remaining = _number(
                ctx.get("calories_remaining_kcal")
                if ctx.get("calories_remaining_kcal") is not None
                else remaining_nutrients.get("calories_kcal")
            )
            consumed = _number(
                ctx.get("calories_consumed_kcal")
                if ctx.get("calories_consumed_kcal") is not None
                else current_consumption.get("calories_kcal")
            )

            if target is not None and target > 0:
                if remaining is not None:
                    out["calories_below_target"] = remaining > 0
                elif consumed is not None:
                    out["calories_below_target"] = consumed < target

    # El objetivo equilibrado solo se determina si hay información
    # explícita sobre el objetivo del usuario.
    if "balanced_goal" in valid:
        if "balanced_goal" in ctx:
            out["balanced_goal"] = _strict_bool(
                ctx["balanced_goal"],
                field="balanced_goal",
            )
        else:
            goal = str(
                ctx.get("primary_goal")
                or ctx.get("goal")
                or _goal_value(ctx, "primary_goal")
                or ""
            ).strip().lower()

            if goal:
                out["balanced_goal"] = goal in {
                    "balanced",
                    "maintenance",
                    "general_health",
                    "equilibrado",
                    "alimentacion_equilibrada",
                    "salud_general",
                }

    return out


def _map_recommendation_confidence(
    ctx: Dict[str, Any],
    valid: set,
) -> Dict[str, bool]:
    out: Dict[str, bool] = {}

    image_relevant = ctx.get("image_relevant", True)

    if type(image_relevant) is not bool:
        raise TypeError("image_relevant debe ser bool.")

    if image_relevant and "high_vision_confidence" in valid:
        if "high_vision_confidence" in ctx:
            out["high_vision_confidence"] = _strict_bool(
                ctx["high_vision_confidence"],
                field="high_vision_confidence",
            )
        elif "vision_confidence" in ctx:
            confidence = _number(ctx["vision_confidence"])

            if confidence is not None and 0 <= confidence <= 1:
                out["high_vision_confidence"] = confidence >= 0.75
            else:
                raise ValueError(
                    "vision_confidence debe ser un número entre 0 y 1."
                )

    for key in (
        "nutrition_data_available",
        "context_complete",
        "evidence_consistent",
    ):
        _copy_bool(ctx, out, valid, key)

    return out


_CONTEXT_MAPPERS = {
    "meal_suitability": _map_meal_suitability,
    "nutritional_priority": _map_nutritional_priority,
    "recommendation_confidence": _map_recommendation_confidence,
}
