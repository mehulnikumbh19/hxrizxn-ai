from __future__ import annotations
import json
import httpx
from dataclasses import dataclass
from app.core.config import Settings


@dataclass(frozen=True)
class ModelRequest:
    system_prompt: str
    user_payload: dict
    schema_name: str


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
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)


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
            response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)


def get_model_provider(settings: Settings) -> ModelProvider:
    if settings.demo_mode:
        return MockModelProvider()
    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        return AzureFoundryModelProvider(settings)
    if settings.openai_api_key:
        return OpenAIModelProvider(settings)
    return MockModelProvider()

