"""Unit tests for the OpenRouterClient adapter in isolation (no network, no
quota spent). These exercise the actual HTTP request/response handling code
path against OpenRouter's OpenAI-compatible chat-completions contract,
complementing test_ai_brief.py's higher-level stub-based service tests.
"""

from __future__ import annotations

import json

import httpx
import pytest

from app.errors import ApplicationError, ApplicationErrorCode
from app.services import ai_client as ai_client_module
from app.services.ai_client import OpenRouterClient


class FakeResponse:
    def __init__(self, status_code=200, json_body=None):
        self.status_code = status_code
        self._json_body = json_body

    def json(self):
        return self._json_body


def chat_completion_envelope(content: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


@pytest.fixture
def client():
    return OpenRouterClient(
        api_key="sk-unique-secret-token-zzz9",
        base_url="https://openrouter.ai/api/v1",
        model="anthropic/claude-sonnet-4.6",
    )


def test_successful_response_is_parsed_into_brief_content(monkeypatch, client):
    response_body = (
        '{"facts": ["Total spend is 1,000 THB"], '
        '"items_to_verify": ["Confirm lead source attribution"], '
        '"next_experiment_proposals": ["Test a new landing page"]}'
    )

    def fake_post(url, json, headers, timeout):
        assert url == "https://openrouter.ai/api/v1/chat/completions"
        assert headers["Authorization"] == "Bearer sk-unique-secret-token-zzz9"
        assert json["model"] == "anthropic/claude-sonnet-4.6"
        assert json["messages"][0]["role"] == "system"
        assert json["messages"][1]["role"] == "user"
        assert "facts" in json["messages"][1]["content"]  # structured context, not raw rows
        return FakeResponse(200, chat_completion_envelope(response_body))

    monkeypatch.setattr(ai_client_module.httpx, "post", fake_post)

    content = client.generate_brief({"facts": "x"})
    assert content.facts == ["Total spend is 1,000 THB"]
    assert content.items_to_verify == ["Confirm lead source attribution"]
    assert content.next_experiment_proposals == ["Test a new landing page"]


def test_json_wrapped_in_markdown_fence_is_still_parsed(monkeypatch, client):
    fenced = (
        "```json\n"
        '{"facts": ["a"], "items_to_verify": ["b"], "next_experiment_proposals": ["c"]}\n'
        "```"
    )
    monkeypatch.setattr(
        ai_client_module.httpx,
        "post",
        lambda *a, **k: FakeResponse(200, chat_completion_envelope(fenced)),
    )
    content = client.generate_brief({})
    assert content.facts == ["a"]


def test_malformed_response_missing_required_key_raises_ai_upstream_error(monkeypatch, client):
    body = json.dumps({"facts": ["only facts, missing other sections"]})
    monkeypatch.setattr(
        ai_client_module.httpx,
        "post",
        lambda *a, **k: FakeResponse(200, chat_completion_envelope(body)),
    )

    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR


def test_field_that_is_a_string_instead_of_a_list_is_rejected(monkeypatch, client):
    body = json.dumps(
        {"facts": "not a list", "items_to_verify": [], "next_experiment_proposals": []}
    )
    monkeypatch.setattr(
        ai_client_module.httpx,
        "post",
        lambda *a, **k: FakeResponse(200, chat_completion_envelope(body)),
    )

    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR


def test_non_json_message_content_raises_ai_upstream_error(monkeypatch, client):
    monkeypatch.setattr(
        ai_client_module.httpx,
        "post",
        lambda *a, **k: FakeResponse(200, chat_completion_envelope("not json at all")),
    )
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR


def test_unexpected_envelope_shape_raises_ai_upstream_error(monkeypatch, client):
    monkeypatch.setattr(
        ai_client_module.httpx, "post", lambda *a, **k: FakeResponse(200, {"unexpected": True})
    )
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR


def test_unauthorized_response_raises_ai_upstream_error(monkeypatch, client):
    monkeypatch.setattr(ai_client_module.httpx, "post", lambda *a, **k: FakeResponse(401, {}))
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR
    assert "unauthorized" in exc_info.value.message.lower()


def test_rate_limited_response_raises_ai_upstream_error(monkeypatch, client):
    monkeypatch.setattr(ai_client_module.httpx, "post", lambda *a, **k: FakeResponse(429, {}))
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR
    assert "rate limit" in exc_info.value.message.lower()


def test_provider_server_error_raises_ai_upstream_error(monkeypatch, client):
    monkeypatch.setattr(ai_client_module.httpx, "post", lambda *a, **k: FakeResponse(503, {}))
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR
    assert "503" in exc_info.value.message


def test_timeout_raises_ai_upstream_error(monkeypatch, client):
    def fake_post(*args, **kwargs):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(ai_client_module.httpx, "post", fake_post)
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR
    assert "timed out" in exc_info.value.message.lower()


def test_connection_error_raises_ai_upstream_error(monkeypatch, client):
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(ai_client_module.httpx, "post", fake_post)
    with pytest.raises(ApplicationError) as exc_info:
        client.generate_brief({})
    assert exc_info.value.code == ApplicationErrorCode.AI_UPSTREAM_ERROR


def test_secret_never_appears_in_outgoing_request_body(monkeypatch, client):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["json"] = json
        captured["headers"] = headers
        body = '{"facts": [], "items_to_verify": [], "next_experiment_proposals": []}'
        return FakeResponse(200, chat_completion_envelope(body))

    monkeypatch.setattr(ai_client_module.httpx, "post", fake_post)
    client.generate_brief({"totals": {"spend_thb": 1.0}})

    # The secret must only travel in the Authorization header, never the JSON body.
    assert "sk-unique-secret-token-zzz9" not in str(captured["json"])
    assert captured["headers"]["Authorization"] == "Bearer sk-unique-secret-token-zzz9"
