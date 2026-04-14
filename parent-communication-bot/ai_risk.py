from ai_service import call_llm

RISK_PROMPT = """
Explain the following risk indicators to a parent.
Be supportive and non-judgmental.

Indicators:
{indicators}
"""

def ai_explain_risk(indicators: str) -> str:
    return call_llm(RISK_PROMPT.format(indicators=indicators))