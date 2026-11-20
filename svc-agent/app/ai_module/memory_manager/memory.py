
from collections import defaultdict

#_store: dict[str, list[dict[str, str]]] = defaultdict(list)

#MAX_TURNS = 10

class Memory:
    def __init__(self, session_id: str = None, MAX_TURNS = 10, _store: dict[str, list[dict[str, str]]] = defaultdict(list)):
        self.session_id = session_id
        self.MAX_TURNS = MAX_TURNS
        self._store = _store

    def get_history(self) -> list[dict[str, str]]:
        """Devuelve el historial de la sesión (puede estar vacío)."""
        return list(self._store.get(self.session_id, []))

    def add_message(self, role: str, content: str) -> None:
        """Añade un mensaje al historial y recorta si excede el límite."""
        self._store[self.session_id].append({"role": role, "content": content})

        max_messages = self.MAX_TURNS * 2
        if len(self._store[self.session_id]) > max_messages:
            self._store[self.session_id] = self._store[self.session_id][-max_messages:]

    def clear_session(self) -> None:
        """Borra el historial de una sesión."""
        self._store.pop(self.session_id, None)

    def get_last_messages(self, limit: int = 5):
        """Get a specific number of messages starting from the last one saved."""
        full_history = self.get_history()
        cropped_list = full_history[-len(full_history):] if len(full_history) < limit else full_history[-limit:]
        return cropped_list
