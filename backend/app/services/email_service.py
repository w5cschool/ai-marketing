import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.audit_log import AuditLog
from app.models.email_campaign import EmailCampaign
from app.models.email_event import EmailEvent
from app.models.email_message import EmailMessage
from app.models.influencer import Influencer

try:
    import resend
except ImportError:  # pragma: no cover - exercised in local envs without resend installed.
    resend = None


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if self.settings.resend_api_key and resend is not None:
            resend.api_key = self.settings.resend_api_key

    async def send_campaign_messages(
        self,
        db: AsyncSession,
        campaign: EmailCampaign,
        influencers: list[Influencer],
        subject: str,
        body: str,
        user_id: str,
    ) -> int:
        accepted = 0
        interval = 60 / max(1, campaign.send_rate_limit)

        today_count_q: Select = select(func.count(EmailMessage.id)).where(
            EmailMessage.sent_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        )
        today_sent = int((await db.execute(today_count_q)).scalar_one())

        for influencer in influencers:
            if influencer.unsubscribed_at is not None or not influencer.email:
                continue
            if today_sent >= self.settings.daily_send_limit:
                break

            payload_body = self._append_unsubscribe(body, influencer.id)
            message = EmailMessage(
                campaign_id=campaign.id,
                influencer_id=influencer.id,
                to_email=influencer.email,
                subject=subject,
                body=payload_body,
                status="pending",
            )
            db.add(message)
            await db.flush()

            ok, provider_id = await self._send_with_retry(influencer.email, subject, payload_body)
            message.status = "sent" if ok else "failed"
            message.provider_message_id = provider_id
            message.sent_at = datetime.now(timezone.utc) if ok else None

            db.add(
                AuditLog(
                    user_id=user_id,
                    action="email_message_send",
                    entity_type="email_message",
                    entity_id=message.id,
                    detail={"status": message.status, "to": influencer.email},
                )
            )
            accepted += 1 if ok else 0
            today_sent += 1 if ok else 0
            await asyncio.sleep(interval)

        campaign.accepted_count = accepted
        campaign.status = "done"
        return accepted

    async def _send_with_retry(self, to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
        if not self.settings.resend_api_key or resend is None:
            return True, "mock-message-id"

        backoff = 1
        for _ in range(3):
            try:
                resp = await asyncio.to_thread(
                    resend.Emails.send,
                    {
                        "from": self.settings.resend_from_email,
                        "to": [to_email],
                        "subject": subject,
                        "html": body.replace("\n", "<br/>")
                    },
                )
                return True, str(resp.get("id"))
            except Exception:
                await asyncio.sleep(backoff)
                backoff *= 2

        return False, None

    def verify_webhook_signature(self, payload: bytes, signature: str | None, secret: str | None) -> bool:
        if not secret:
            return True
        if not signature:
            return False
        digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)

    async def process_webhook_event(self, db: AsyncSession, payload: dict) -> bool:
        provider_event_id = str(payload.get("id")) if payload.get("id") else None
        if provider_event_id:
            existing = await db.execute(select(EmailEvent).where(EmailEvent.provider_event_id == provider_event_id))
            if existing.scalar_one_or_none() is not None:
                return False

        data = payload.get("data", {})
        message_id = data.get("email_id") or data.get("message_id")
        if not message_id:
            return False

        msg = await db.execute(select(EmailMessage).where(EmailMessage.provider_message_id == message_id))
        message = msg.scalar_one_or_none()
        if not message:
            return False

        event = EmailEvent(
            message_id=message.id,
            provider_event_id=provider_event_id,
            event_type=payload.get("type", "unknown"),
            raw_payload=payload,
        )
        db.add(event)
        return True

    def _append_unsubscribe(self, body: str, influencer_id) -> str:
        return f"{body}\n\n---\nUnsubscribe: https://example.com/unsubscribe/{influencer_id}"
