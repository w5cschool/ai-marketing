import pytest

from app.config import get_settings
from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_ai_service_fallback_when_no_key(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    service = AIService()
    result = await service.generate_email_draft(
        goal="Invite creator for partnership",
        tone="professional",
        language="en",
        context={"influencers": []},
    )

    assert "subject" in result
    assert "body" in result
    assert isinstance(result.get("variables"), dict)
