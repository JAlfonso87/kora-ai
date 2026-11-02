
from collections import defaultdict

_store: dict[str, list[dict[str, str]]] = defaultdict(list)

MAX_TURNS = 10


def get_history(session_id: str) -> list[dict[str, str]]:
    """Devuelve el historial de la sesión (puede estar vacío)."""
    return list(_store.get(session_id, []))


def add_message(session_id: str, role: str, content: str) -> None:
    """Añade un mensaje al historial y recorta si excede el límite."""
    _store[session_id].append({"role": role, "content": content})

    max_messages = MAX_TURNS * 2
    if len(_store[session_id]) > max_messages:
        _store[session_id] = _store[session_id][-max_messages:]


def clear_session(session_id: str) -> None:
    """Borra el historial de una sesión."""
    _store.pop(session_id, None)
