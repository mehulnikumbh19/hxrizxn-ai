from __future__ import annotations

from app.core.config import Settings
from app.providers.model import MockModelProvider, get_model_provider


def test_demo_mode_uses_mock_provider_even_when_live_keys_are_configured():
    settings = Settings(
        demo_mode=True,
        openai_api_key="sk-test",
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_api_key="test-key",
    )

    provider = get_model_provider(settings)

    assert isinstance(provider, MockModelProvider)
