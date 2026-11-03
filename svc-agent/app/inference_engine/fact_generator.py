from typing import Any
from pydantic import BaseModel


# Function responsible of splitting pre-existing NutritionalContext into a list of facts.
def build_fact_base(context: BaseModel) -> dict[str, Any]:
    facts: dict[str, Any] = {}

    def process(value: Any, prefix: str = "") -> None:
        if isinstance(value, BaseModel):
            # Validates if the current value is still a model archtype.

            for name in type(value).model_fields: 
                # For every field in the NutritionalContext model:
                child = getattr(value, name)
                # Get the atribute of the current model with the retrieved name.
                path = f"{prefix}.{name}" if prefix else name
                # Build a partial/full path depending on the atribute name and previous prefix if applicable.
                process(child, path)
                # Executes this operation on loop until reaching a non-model archtype attribute.

        elif value is not None:
            # If the current value is not a model archtype, it is classified as a final attribute, therefore, 
            #    its value is added as a fully formed fact.
            facts[prefix] = value

    process(context)

    return facts
