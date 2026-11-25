from app.context_module.nutritional_profile.models import NutritionalContext

class NutritionalContextManager:
    def __init__(self):
        self.contexts: dict[str, NutritionalContext] = {}

    def get_context(self, session_id: str) -> NutritionalContext:
        if session_id not in self.contexts:
            self.contexts[session_id] = NutritionalContext()
        return self.contexts[session_id]

    def save_context(self, session_id: str, context: NutritionalContext) -> None:
        self.contexts[session_id] = context