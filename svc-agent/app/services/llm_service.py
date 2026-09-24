from dotenv import load_dotenv
import os

from groq import Groq


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



def generate_response(message: str) -> str:

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "Eres Kora AI, un asistente especializado en nutrición."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return response.choices[0].message.content