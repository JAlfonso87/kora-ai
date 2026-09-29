from app.nutritional_context.nutritional_context_models import NutritionalContext

contexts: dict[str, NutritionalContext] = {}

def get_context(session_id: str) -> NutritionalContext:
    if session_id not in contexts:
        contexts[session_id] = NutritionalContext()

    return contexts[session_id]

def save_context(
    session_id: str,
    context: NutritionalContext,
) -> None:
    print(" << INICIANDO GUARDADO DE CONTEXTO... >> ")
    contexts[session_id] = context