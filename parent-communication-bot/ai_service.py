import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

def call_llm(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120  # ⬅️ CRITICAL CHANGE
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        print("⚠️ AI_SERVICE_ERROR:", str(e))
        return None
