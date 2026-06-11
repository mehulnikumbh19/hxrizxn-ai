from __future__ import annotations
import json
from collections.abc import Callable
import httpx
from dataclasses import dataclass
from app.core.config import Settings


class ModelOutputError(RuntimeError):
    """Raised when a model response cannot be parsed as JSON after retries."""


@dataclass(frozen=True)
class ModelRequest:
    system_prompt: str
    user_payload: dict
    schema_name: str


def _request_json_with_retry(do_request: Callable[[], httpx.Response], attempts: int = 2) -> dict:
    """Issue the request and parse the JSON content, retrying once on malformed JSON.

    Live models occasionally return non-JSON or truncated content; a single retry
    usually self-corrects. After exhausting attempts we raise ModelOutputError so
    the orchestrator can fall back instead of crashing the whole workflow.
    """
    last_error: Exception | None = None
    for _ in range(attempts):
        response = do_request()
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError) as exc:
            last_error = exc
    raise ModelOutputError(f"Model returned non-JSON content after {attempts} attempts: {last_error}")


class ModelProvider:
    name = "base"

    def complete_json(self, request: ModelRequest) -> dict:
        raise NotImplementedError


class MockModelProvider(ModelProvider):
    name = "mock"

    def complete_json(self, request: ModelRequest) -> dict:
        return {"provider": self.name, "schema_name": request.schema_name, "mock": True}


class AzureFoundryModelProvider(ModelProvider):
    name = "azure-foundry"

    def __init__(self, settings: Settings):
        self.settings = settings

    def complete_json(self, request: ModelRequest) -> dict:
        if not (self.settings.azure_openai_endpoint and self.settings.azure_openai_api_key):
            return MockModelProvider().complete_json(request)

        endpoint = self.settings.azure_openai_endpoint.rstrip("/")
        if not endpoint.startswith(("http://", "https://")):
            endpoint = f"https://{endpoint}"

        if "/openai/deployments" in endpoint:
            url = endpoint
        else:
            url = f"{endpoint}/openai/deployments/{self.settings.azure_openai_deployment}/chat/completions?api-version={self.settings.azure_openai_api_version}"

        headers = {
            "api-key": self.settings.azure_openai_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": json.dumps(request.user_payload)},
            ],
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=60.0) as client:
            return _request_json_with_retry(lambda: client.post(url, headers=headers, json=payload))


class OpenAIModelProvider(ModelProvider):
    name = "openai"

    def __init__(self, settings: Settings):
        self.settings = settings

    def complete_json(self, request: ModelRequest) -> dict:
        if not self.settings.openai_api_key:
            return MockModelProvider().complete_json(request)

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.settings.openai_model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": json.dumps(request.user_payload)},
            ],
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=60.0) as client:
            return _request_json_with_retry(
                lambda: client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            )


def get_model_provider(settings: Settings) -> ModelProvider:
    if settings.demo_mode:
        return MockModelProvider()
    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        return AzureFoundryModelProvider(settings)
    if settings.openai_api_key:
        return OpenAIModelProvider(settings)
    return MockModelProvider()

