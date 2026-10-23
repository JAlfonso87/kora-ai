
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class TruthValue(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


Operator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "contains",
    "exists",
    "contains_any_fact",
    "in_fact",
    "unknown_or_missing",
]


class Condition(BaseModel):
    # Identifier of the fact to evaluate.
    fact: str = Field(
        min_length=1,
        description="Identifier of the fact in the facts base.",
    )

    operator: Operator

    # Literal comparison value, when applicable.
    value: Any = None

    # Identifier of another fact used for comparison.
    value_from_fact: str | None = None

    @model_validator(mode="after")
    def validate_condition(self):
        if self.value_from_fact is not None and not self.value_from_fact.strip():
            raise ValueError("'value_from_fact' cannot be empty.")

        if self.operator in {"contains_any_fact", "in_fact"}:
            if not self.value_from_fact:
                raise ValueError(
                    f"Operator '{self.operator}' requires 'value_from_fact'."
                )
            if self.value is not None:
                raise ValueError(
                    f"Operator '{self.operator}' uses 'value_from_fact', "
                    "not 'value'."
                )

        elif self.value_from_fact is not None:
            if self.operator not in {"eq", "ne", "gt", "gte", "lt", "lte"}:
                raise ValueError(
                    f"Operator '{self.operator}' does not support "
                    "'value_from_fact'."
                )
            if self.value is not None:
                raise ValueError(
                    "Use either 'value' or 'value_from_fact', not both."
                )

        elif self.operator not in {"exists", "unknown_or_missing"}:
            if self.value is None:
                raise ValueError(
                    f"Operator '{self.operator}' requires a non-None value "
                    "or a valid 'value_from_fact'."
                )

        # For exists and unknown_or_missing, an optional boolean value
        # is accepted for compatibility with the current rules.json.
        if self.operator in {"exists", "unknown_or_missing"}:
            if self.value is not None and not isinstance(self.value, bool):
                raise ValueError(
                    f"Operator '{self.operator}' accepts only a boolean "
                    "value when one is provided."
                )
            if self.value_from_fact is not None:
                raise ValueError(
                    f"Operator '{self.operator}' does not use "
                    "'value_from_fact'."
                )

        return self


class Conclusion(BaseModel):
    type: str = Field(min_length=1)
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class Rule(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = "general"
    description: str = ""
    conditions: list[Condition] = Field(min_length=1)
    conclusion: Conclusion
    priority: int = 100
    enabled: bool = True
    notes: str | None = None


class ConditionResult(BaseModel):
    fact: str
    operator: str
    expected: Any = None
    actual: Any = None
    status: TruthValue
    explanation: str
    missing_facts: list[str] = Field(default_factory=list)


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    status: TruthValue
    conclusion: Conclusion | None = None
    conditions: list[ConditionResult]
    missing_facts: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    activated_rules: list[str] = Field(default_factory=list)
    conclusions: list[Conclusion] = Field(default_factory=list)
    rule_results: list[RuleResult] = Field(default_factory=list)
    missing_facts: list[str] = Field(default_factory=list)
