import json
from ai_service import call_llm

INTENT_PROMPT = """
You are an intent classifier for a school parent assistant.

Choose EXACTLY ONE intent from:
attendance, homework, grades, summary, fee, greeting, unknown.

Rules:
- Questions about overall progress, performance, wellbeing,
  or "how is my child doing" MUST be classified as "summary".
- Only short greetings like "hi", "hello", "hey" alone are "greeting".
- Do NOT answer the question.
- Return JSON ONLY in this format:
  {{ "intent": "<intent_name>" }}

Message:
"{message}"
"""

def detect_intent(message: str) -> dict:
    try:
        raw = call_llm(INTENT_PROMPT.format(message=message))

        if not raw:
            return {"intent": "unknown"}

        data = json.loads(raw)

        intent = data.get("intent")
        if intent not in {
            "attendance", "homework", "grades",
            "summary", "fee", "greeting", "unknown"
        }:
            return {"intent": "unknown"}

        return {"intent": intent}

    except Exception as e:
        print("⚠️ INTENT_DETECTION_ERROR:", e)
        return {"intent": "unknown"}