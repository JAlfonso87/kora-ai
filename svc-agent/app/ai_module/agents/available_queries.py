from typing import Literal, TypeAlias

PlannerAvailableQueries: TypeAlias = Literal[
    "UPDATE_FOOD_CONTEXT", 
    "CALCULATE_CURRENT_CONSUMPTION", 
    "UPDATE_NUTRITIONAL_GOALS",
    "CALCULATE_REMAINING_NUTRIENTS",
    "RAG_QUERY"
] | None
