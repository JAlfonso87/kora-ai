from app.context_module.food_profile.models import FoodContext

class FoodContextManager:
    def __init__(self):
        self.contexts: dict[str, FoodContext] = {}

    def get_context(self, session_id: str) -> FoodContext:
        if session_id not in self.contexts:
            self.contexts[session_id] = FoodContext()
        return self.contexts[session_id]

    def save_context(self, session_id: str, context: FoodContext) -> None:
        self.contexts[session_id] = context