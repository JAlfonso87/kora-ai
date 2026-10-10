
import requests
from django.conf import settings


def call_agent(
    message: str,
    session_id: str | None = None,
    nutritional_context: dict | None = None,
) -> dict:
    agent_url = settings.AGENT_SERVICE_URL.rstrip("/")

    payload = {
        "message": message,
        "session_id": session_id,
        "nutritional_context": nutritional_context,
    }

    response = requests.post(
        f"{agent_url}/agent/query",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()
