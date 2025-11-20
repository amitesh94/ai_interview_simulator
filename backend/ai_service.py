import os
from dotenv import load_dotenv
import requests

# Load .env into environment (if present)
load_dotenv()

# If using OpenAI API — set environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask_ai(prompt: str) -> str:
    """
    Uses OpenAI Chat API (or compatible API).
    If no key provided, returns dummy message.
    """

    if not OPENAI_API_KEY:
        return "AI model not configured. Please set OPENAI_API_KEY."

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",   # fast + cheap model
        "messages": [
            {"role": "system", "content": "You are a professional HR interviewer. Ask one question at a time."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()

        return res_json["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error calling AI: {str(e)}"
