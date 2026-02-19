import json

from openai import AsyncOpenAI

from app.config import get_settings


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None
        if self.settings.openai_api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            except Exception:
                # Degrade gracefully in local/dev env with incompatible dependency combos.
                self.client = None

    async def generate_email_draft(self, goal: str, tone: str, language: str, context: dict) -> dict:
        if self.client is None:
            return {
                "subject": f"{goal[:60]} - Collaboration Opportunity",
                "body": "Hello {{name}},\n\nWe admire your content and want to explore collaboration.\n\nBest regards,\nTeam",
                "variables": {"name": "influencer_name", "brand": "brand_name"},
            }

        prompt = {
            "goal": goal,
            "tone": tone,
            "language": language,
            "context": context,
            "output_format": {"subject": "string", "body": "string", "variables": "object"},
        }
        completion = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "你是一个 B2B outreach 邮件专家。"},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            temperature=0.7,
        )

        content = completion.choices[0].message.content or "{}"
        data = json.loads(content)
        return {
            "subject": data.get("subject", "Collaboration Opportunity"),
            "body": data.get("body", ""),
            "variables": data.get("variables", {}),
        }
