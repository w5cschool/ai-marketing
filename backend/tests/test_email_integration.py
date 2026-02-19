import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db
from app.config import get_settings
from app.main import app
from app.models.email_campaign import EmailCampaign
from app.models.email_event import EmailEvent
from app.models.email_message import EmailMessage
from app.models.influencer import Influencer
from app.services.email_service import EmailService


class _ResultStub:
    def __init__(self, one=None):
        self._one = one

    def scalar_one_or_none(self):
        return self._one

    def scalar_one(self):
        return self._one


class FakeWebhookDB:
    def __init__(self) -> None:
        self.events_by_provider_id: dict[str, EmailEvent] = {}
        self.messages_by_provider_message_id: dict[str, EmailMessage] = {}
        msg = EmailMessage(
            id=uuid.uuid4(),
            campaign_id=uuid.uuid4(),
            influencer_id=uuid.uuid4(),
            to_email="creator@example.com",
            subject="hello",
            body="hello body",
            status="sent",
            provider_message_id="provider-msg-1",
        )
        self.messages_by_provider_message_id[msg.provider_message_id or ""] = msg

    async def execute(self, statement):
        params = statement.compile().params
        param_values = list(params.values())
        sql = str(statement)
        if "FROM email_events" in sql:
            provider_event_id = str(param_values[0]) if param_values else ""
            return _ResultStub(self.events_by_provider_id.get(provider_event_id))
        if "FROM email_messages" in sql:
            provider_message_id = str(param_values[0]) if param_values else ""
            return _ResultStub(self.messages_by_provider_message_id.get(provider_message_id))
        return _ResultStub(None)

    def add(self, obj):
        if isinstance(obj, EmailEvent) and obj.provider_event_id:
            self.events_by_provider_id[obj.provider_event_id] = obj

    async def commit(self):
        return None


class FakeCampaignDB:
    def __init__(self, today_sent: int = 0) -> None:
        self.today_sent = today_sent
        self.added = []

    async def execute(self, _statement):
        return _ResultStub(self.today_sent)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        return None


@pytest.mark.asyncio
async def test_webhook_idempotency() -> None:
    fake_db = FakeWebhookDB()

    async def override_db() -> AsyncGenerator[FakeWebhookDB, None]:
        yield fake_db

    app.dependency_overrides[get_db] = override_db

    payload = {
        "id": "evt-1",
        "type": "delivered",
        "data": {"email_id": "provider-msg-1"},
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/api/v1/webhooks/resend", json=payload)
        second = await client.post("/api/v1/webhooks/resend", json=payload)

    app.dependency_overrides.clear()

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["saved"] is True
    assert second.json()["saved"] is False


@pytest.mark.asyncio
async def test_send_campaign_respects_daily_limit_and_rate(monkeypatch) -> None:
    service = EmailService()
    service.settings.daily_send_limit = 1

    delays: list[float] = []

    async def fake_sleep(seconds: float):
        delays.append(seconds)

    async def fake_send_with_retry(_to: str, _subject: str, _body: str):
        return True, "msg-1"

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(service, "_send_with_retry", fake_send_with_retry)

    campaign = EmailCampaign(id=uuid.uuid4(), draft_id=uuid.uuid4(), status="sending", send_rate_limit=30)
    influencers = [
        Influencer(
            id=uuid.uuid4(),
            platform="youtube",
            platform_user_id="u1",
            display_name="one",
            profile_url="https://youtube.com/@one",
            follower_count=1000,
            email="one@example.com",
            saved_by="tester",
        ),
        Influencer(
            id=uuid.uuid4(),
            platform="youtube",
            platform_user_id="u2",
            display_name="two",
            profile_url="https://youtube.com/@two",
            follower_count=2000,
            email="two@example.com",
            saved_by="tester",
        ),
    ]

    fake_db = FakeCampaignDB(today_sent=0)
    accepted = await service.send_campaign_messages(
        db=fake_db,
        campaign=campaign,
        influencers=influencers,
        subject="subject",
        body="body",
        user_id="u",
    )

    assert accepted == 1
    assert campaign.accepted_count == 1
    assert delays == [2.0]


@pytest.mark.asyncio
async def test_send_with_retry_exponential_backoff(monkeypatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    get_settings.cache_clear()
    from app.services import email_service as email_service_module

    call_count = {"n": 0}
    sleep_delays: list[int] = []

    class _FakeEmails:
        @staticmethod
        def send(_payload):
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise RuntimeError("temporary error")
            return {"id": "provider-123"}

    class _FakeResend:
        api_key = ""
        Emails = _FakeEmails

    monkeypatch.setattr(email_service_module, "resend", _FakeResend)
    service = EmailService()

    async def fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    async def fake_sleep(seconds: int):
        sleep_delays.append(seconds)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    ok, message_id = await service._send_with_retry("to@example.com", "s", "b")

    assert ok is True
    assert message_id == "provider-123"
    assert call_count["n"] == 3
    assert sleep_delays == [1, 2]
