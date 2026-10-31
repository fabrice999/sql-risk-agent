
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5-coder:3b"

OLLAMA_TIMEOUT = 300


class LLMError(Exception):
    """Raised when local LLM analysis fails."""


def explain_risk(
    sql: str,
    risk_result: dict,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Ask the local LLM to explain an existing SQL risk assessment.

    The deterministic risk engine remains authoritative.
    The LLM cannot override its verdict or score.
    """

    system_prompt = """
You are a PostgreSQL DBA assistant.

Explain the supplied deterministic SQL risk assessment.

Rules:
- Never execute SQL.
- Never change the verdict or score.
- Do not invent PostgreSQL statistics.
- Treat estimated rows as estimates, not actual counts.
- Ordinary SELECT statements are not blocked by DELETE row locks.
- Keep the explanation concise.

Return a JSON object containing:
{
  "explanation": "One short sentence",
  "recommendations": ["One short recommendation"]
}
"""

    user_prompt = json.dumps({
        "sql": sql,
        "risk_assessment": risk_result,
    })

    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 120,
            "num_ctx": 2048,
        },
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
            data = json.load(response)

        result = json.loads(data["response"])

    except (URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
        raise LLMError(f"Ollama analysis failed: {exc}") from exc

    elapsed = time.perf_counter() - start
    print(f"Ollama execution time: {elapsed:.2f} seconds", file=sys.stderr)
    if not isinstance(result, dict):
        raise LLMError("Ollama returned an invalid JSON object")

    explanation = result.get("explanation")
    recommendations = result.get("recommendations")

    if not isinstance(explanation, str) or not explanation.strip():
        raise LLMError("Ollama response is missing a valid explanation")

    if not isinstance(recommendations, list) or not all(
        isinstance(item, str) for item in recommendations
    ):
        raise LLMError("Ollama response has invalid recommendations")

    return {
        "explanation": explanation,
        "recommendations": recommendations,
    }

