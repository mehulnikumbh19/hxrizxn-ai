from __future__ import annotations

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
        raise NotImplementedError("Azure Foundry runtime is configured as an integration seam for MVP.")


class OpenAIModelProvider(ModelProvider):
    name = "openai"

    def __init__(self, settings: Settings):
        self.settings = settings

    def complete_json(self, request: ModelRequest) -> dict:
        if not self.settings.openai_api_key:
            return MockModelProvider().complete_json(request)
        raise NotImplementedError("Direct OpenAI fallback is scaffolded behind the provider abstraction.")


def get_model_provider(settings: Settings) -> ModelProvider:
    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        return AzureFoundryModelProvider(settings)
    if settings.openai_api_key:
        return OpenAIModelProvider(settings)
    return MockModelProvider()

