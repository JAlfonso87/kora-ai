from typing import Literal

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