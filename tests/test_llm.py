
import json
from unittest.mock import patch

import pytest

from sql_risk_agent.llm import explain_risk, LLMError


# Simulate the HTTP response returned by Ollama.
class FakeResponse:

    def __init__(self, response_data):
        self.response_data = response_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.response_data).encode("utf-8")


# Test 1: Successful LLM response
def test_explain_risk_success():

    ollama_response = {
        "response": json.dumps({
            "explanation": "The DELETE may affect many rows.",
            "recommendations": [
                "Verify the WHERE condition.",
                "Consider deleting in batches."
            ]
        })
    }

    with patch(
        "sql_risk_agent.llm.urlopen",
        return_value=FakeResponse(ollama_response),
    ) as mock_urlopen:

        result = explain_risk(
            sql="DELETE FROM orders WHERE id > 0;",
            risk_result={
                "verdict": "block",
                "score": 90,
            },
        )

    assert result["explanation"] == (
        "The DELETE may affect many rows."
    )

    assert result["recommendations"] == [
        "Verify the WHERE condition.",
        "Consider deleting in batches."
    ]

    # Verify that the HTTP function was called.
    mock_urlopen.assert_called_once()


# Test 2: Ollama returns invalid JSON
def test_explain_risk_invalid_json():

    ollama_response = {
        "response": "This is not valid JSON"
    }

    with patch(
        "sql_risk_agent.llm.urlopen",
        return_value=FakeResponse(ollama_response),
    ):

        with pytest.raises(LLMError):
            explain_risk(
                sql="DELETE FROM orders;",
                risk_result={
                    "verdict": "block",
                    "score": 90,
                },
            )


# Test 3: Ollama returns an invalid explanation
def test_explain_risk_missing_explanation():

    ollama_response = {
        "response": json.dumps({
            "recommendations": [
                "Check the SQL statement."
            ]
        })
    }

    with patch(
        "sql_risk_agent.llm.urlopen",
        return_value=FakeResponse(ollama_response),
    ):

        with pytest.raises(
            LLMError,
            match="missing a valid explanation",
        ):
            explain_risk(
                sql="DELETE FROM orders;",
                risk_result={
                    "verdict": "block",
                    "score": 90,
                },
            )


# Test 4: Ollama connection timeout
def test_explain_risk_timeout():

    with patch(
        "sql_risk_agent.llm.urlopen",
        side_effect=TimeoutError("timed out"),
    ):

        with pytest.raises(
            LLMError,
            match="timed out",
        ):
            explain_risk(
                sql="DELETE FROM orders;",
                risk_result={
                    "verdict": "block",
                    "score": 90,
                },
            )


# Test 5: Ollama returns invalid recommendations
def test_explain_risk_invalid_recommendations():

    ollama_response = {
        "response": json.dumps({
            "explanation": "Large DELETE operation.",
            "recommendations": "Check the WHERE clause."
        })
    }

    with patch(
        "sql_risk_agent.llm.urlopen",
        return_value=FakeResponse(ollama_response),
    ):

        with pytest.raises(
            LLMError,
            match="invalid recommendations",
        ):
            explain_risk(
                sql="DELETE FROM orders;",
                risk_result={
                    "verdict": "block",
                    "score": 90,
                },
            )

