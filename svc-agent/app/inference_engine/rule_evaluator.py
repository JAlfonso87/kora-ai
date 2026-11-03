
from collections.abc import Mapping
from typing import Any

from app.inference_engine.required_models import (
    Condition,
    ConditionResult,
    EvaluationResult,
    Rule,
    RuleResult,
    TruthValue,
)


def _as_items(value: Any) -> list[Any] | None:
    """Return collection items without treating strings as collections."""
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(value)

    if isinstance(value, str):
        return [value]

    return None


def _normalise(value: Any) -> Any:
    """Normalise strings for case-insensitive food-name comparisons."""
    if isinstance(value, str):
        return value.strip().casefold()
    return value


def _contains(container: Any, item: Any) -> bool:
    """Check membership, normalising string food names."""
    items = _as_items(container)

    if items is not None:
        target = _normalise(item)
        return any(_normalise(candidate) == target for candidate in items)

    if isinstance(container, str) and isinstance(item, str):
        return item.casefold() in container.casefold()

    raise TypeError("The value does not support containment.")


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    """Evaluate a supported comparison between two known values."""
    if operator == "eq":
        return actual == expected

    if operator == "ne":
        return actual != expected

    if operator == "gt":
        return actual > expected

    if operator == "gte":
        return actual >= expected

    if operator == "lt":
        return actual < expected

    if operator == "lte":
        return actual <= expected

    if operator == "in":
        return _contains(expected, actual)

    if operator == "contains":
        return _contains(actual, expected)

    if operator == "in_fact":
        return _contains(expected, actual)

    if operator == "contains_any_fact":
        actual_items = _as_items(actual)
        expected_items = _as_items(expected)

        if actual_items is None or expected_items is None:
            raise TypeError(
                "'contains_any_fact' requires two collections."
            )

        actual_values = {_normalise(item) for item in actual_items}
        expected_values = {_normalise(item) for item in expected_items}

        return bool(actual_values & expected_values)

    raise ValueError(f"Unsupported operator: {operator}")


class RuleEngine:
    def evaluate_condition(
        self,
        condition: Condition,
        facts: Mapping[str, Any],
    ) -> ConditionResult:
        fact_name = condition.fact
        operator = condition.operator

        present = fact_name in facts
        actual = facts.get(fact_name)

        # Check whether the fact is known.
        known = present and actual is not None

        # exists:
        #   no value / True  -> the fact must be known
        #   False            -> the fact must be missing or None
        if operator == "exists":
            expected = condition.value

            matched = (
                known if expected is not False
                else not known
            )

            return ConditionResult(
                fact=fact_name,
                operator=operator,
                expected=expected,
                actual=actual,
                status=(
                    TruthValue.TRUE if matched
                    else TruthValue.FALSE
                ),
                explanation=(
                    "Fact existence condition matched."
                    if matched
                    else "Fact existence condition did not match."
                ),
            )

        # unknown_or_missing:
        #   no value / True  -> fact must be missing or None
        #   False            -> fact must be known
        if operator == "unknown_or_missing":
            expected = condition.value

            is_unknown = not known
            matched = (
                is_unknown if expected is not False
                else not is_unknown
            )

            return ConditionResult(
                fact=fact_name,
                operator=operator,
                expected=expected,
                actual=actual,
                status=(
                    TruthValue.TRUE if matched
                    else TruthValue.FALSE
                ),
                explanation=(
                    "Fact is missing or unknown."
                    if is_unknown
                    else "Fact is known."
                ),
            )

        # Missing or None values cannot be compared safely.
        if not known:
            return ConditionResult(
                fact=fact_name,
                operator=operator,
                expected=condition.value,
                actual=actual,
                status=TruthValue.UNKNOWN,
                explanation=(
                    "Fact is missing or unknown; "
                    "condition was not evaluated."
                ),
            )

        # Resolve either a literal value or another fact.
        if condition.value_from_fact is not None:
            reference = condition.value_from_fact

            if reference not in facts or facts[reference] is None:
                return ConditionResult(
                    fact=fact_name,
                    operator=operator,
                    expected=None,
                    actual=actual,
                    status=TruthValue.UNKNOWN,
                    explanation=(
                        f"Referenced fact '{reference}' is missing "
                        "or unknown."
                    ),
                )

            expected = facts[reference]
        else:
            expected = condition.value

        # Evaluate the comparison.
        try:
            matched = _compare(actual, operator, expected)
        except (TypeError, ValueError, KeyError, AttributeError):
            return ConditionResult(
                fact=fact_name,
                operator=operator,
                expected=expected,
                actual=actual,
                status=TruthValue.UNKNOWN,
                explanation=(
                    "Incompatible values or types; "
                    "condition was not evaluated."
                ),
            )

        return ConditionResult(
            fact=fact_name,
            operator=operator,
            expected=expected,
            actual=actual,
            status=(
                TruthValue.TRUE if matched
                else TruthValue.FALSE
            ),
            explanation=(
                "Condition matched."
                if matched
                else "Condition did not match."
            ),
        )

    def evaluate_rule(
        self,
        rule: Rule,
        facts: Mapping[str, Any],
    ) -> RuleResult:
        results = [
            self.evaluate_condition(condition, facts)
            for condition in rule.conditions
        ]

        statuses = [result.status for result in results]

        # AND semantics:
        # FALSE wins; otherwise UNKNOWN wins over TRUE.
        if TruthValue.FALSE in statuses:
            status = TruthValue.FALSE
        elif TruthValue.UNKNOWN in statuses:
            status = TruthValue.UNKNOWN
        else:
            status = TruthValue.TRUE

        missing = sorted({
            fact
            for result in results
            for fact in result.missing_facts
        })

        return RuleResult(
            rule_id=rule.id,
            rule_name=rule.name,
            status=status,
            conclusion=(
                rule.conclusion
                if status == TruthValue.TRUE
                else None
            ),
            conditions=results,
            missing_facts=missing,
        )

    def evaluate(
        self,
        facts: Mapping[str, Any],
        rules: list[Rule],
    ) -> EvaluationResult:
        ids = [rule.id for rule in rules]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "Rule IDs must be unique in one evaluation."
            )

        enabled_rules = sorted(
            (rule for rule in rules if rule.enabled),
            key=lambda rule: (-rule.priority, rule.id),
        )

        results = [
            self.evaluate_rule(rule, facts)
            for rule in enabled_rules
        ]

        return EvaluationResult(
            activated_rules=[
                result.rule_id
                for result in results
                if result.status == TruthValue.TRUE
            ],
            conclusions=[
                result.conclusion
                for result in results
                if (
                    result.status == TruthValue.TRUE
                    and result.conclusion is not None
                )
            ],
            rule_results=results,
            missing_facts=sorted({
                fact
                for result in results
                for fact in result.missing_facts
            }),
        )
