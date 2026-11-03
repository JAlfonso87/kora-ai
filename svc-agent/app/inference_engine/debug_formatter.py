
import json
from typing import Any

from app.inference_engine.required_models import (
    EvaluationResult,
    TruthValue,
)


# Colores para la terminal.
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "gray": "\033[90m",
}


def _color(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def _value(value: Any) -> str:
    """Format values compactly and preserve readable Unicode."""
    if value is None:
        return "∅ (None)"

    if isinstance(value, TruthValue):
        return value.value.upper()

    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    return repr(value)


def _status(status: TruthValue, color: bool) -> str:
    labels = {
        TruthValue.TRUE: ("[ACTIVADA]", "green"),
        TruthValue.FALSE: ("[NO COINCIDE]", "red"),
        TruthValue.UNKNOWN: ("[DESCONOCIDA]", "yellow"),
    }

    label, shade = labels[status]
    return _color(label, shade, color)


def format_evaluation(
    result: EvaluationResult,
    *,
    show_all: bool = True,
    color: bool = True,
) -> str:
    """Return a readable debug report for an EvaluationResult."""

    lines: list[str] = []
    separator = "=" * 76
    thin_separator = "-" * 76

    all_rules = result.rule_results
    activated = [
        rule for rule in all_rules
        if rule.status == TruthValue.TRUE
    ]
    rejected = [
        rule for rule in all_rules
        if rule.status == TruthValue.FALSE
    ]
    unknown = [
        rule for rule in all_rules
        if rule.status == TruthValue.UNKNOWN
    ]

    # Header and summary.
    lines.extend([
        "",
        _color(separator, "cyan", color),
        _color("             RULE ENGINE — EVALUATION REPORT", "bold", color),
        _color(separator, "cyan", color),
        "",
        f"  Total de reglas evaluadas : {len(all_rules)}",
        _color(
            f"  Reglas activadas          : {len(activated)}",
            "green",
            color,
        ),
        _color(
            f"  Reglas no coincidentes    : {len(rejected)}",
            "red",
            color,
        ),
        _color(
            f"  Reglas indeterminadas     : {len(unknown)}",
            "yellow",
            color,
        ),
        f"  Conclusiones generadas    : {len(result.conclusions)}",
        f"  Hechos desconocidos       : {len(result.missing_facts)}",
        "",
    ])

    # Activated conclusions.
    lines.append(_color("1. CONCLUSIONES ACTIVAS", "bold", color))
    lines.append(thin_separator)

    if not result.conclusions:
        lines.append("  No se generaron conclusiones.")
    else:
        for index, conclusion in enumerate(result.conclusions, start=1):
            lines.extend([
                f"  {index}. [{conclusion.type}] {conclusion.code}",
                f"     {conclusion.message}",
                "",
            ])

    # Missing facts.
    lines.append(_color("2. HECHOS DESCONOCIDOS", "bold", color))
    lines.append(thin_separator)

    if not result.missing_facts:
        lines.append("  No se registraron hechos desconocidos.")
    else:
        for fact in result.missing_facts:
            lines.append(f"  • {fact}")

    # Individual rule details.
    lines.extend([
        "",
        _color("3. DETALLE DE REGLAS", "bold", color),
        thin_separator,
    ])

    rules_to_show = all_rules if show_all else activated

    if not rules_to_show:
        lines.append("  No hay reglas para mostrar.")

    for rule in rules_to_show:
        lines.extend([
            "",
            f"{_status(rule.status, color)} "
            f"{rule.rule_id} — {rule.rule_name}",
            f"  Estado: {rule.status.value.upper()}",
        ])

        if rule.conclusion is not None:
            lines.append(
                f"  Conclusión: {rule.conclusion.code}"
            )

        if rule.missing_facts:
            lines.append(
                "  Hechos desconocidos: "
                + ", ".join(rule.missing_facts)
            )

        for index, condition in enumerate(rule.conditions, start=1):
            lines.append(
                f"    Condición {index}: "
                f"{_status(condition.status, color)}"
            )
            lines.append(f"      Hecho     : {condition.fact}")
            lines.append(f"      Operador  : {condition.operator}")
            lines.append(f"      Esperado  : {_value(condition.expected)}")
            lines.append(f"      Actual    : {_value(condition.actual)}")
            lines.append(f"      Explicación: {condition.explanation}")

            condition_missing = getattr(
                condition, "missing_facts", []
            )
            if condition_missing:
                lines.append(
                    "      Faltantes : "
                    + ", ".join(condition_missing)
                )

    lines.extend([
        "",
        _color(separator, "cyan", color),
        "",
    ])

    return "\n".join(lines)
