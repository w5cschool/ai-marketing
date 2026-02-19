import re
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.search_result import SearchResultRaw

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class YouTubeConnector:
    base_url = "https://www.googleapis.com/youtube/v3"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_and_store(
        self,
        db: AsyncSession,
        task_id: str,
        queries: list[str],
        follower_min: int | None = None,
        follower_max: int | None = None,
        pages: int = 1,
    ) -> int:
        dedup_ids: set[str] = set()
        if not self.settings.youtube_api_key:
            return await self._mock_results(
                db,
                task_id=task_id,
                query=queries[0] if queries else "youtube creator",
                follower_min=follower_min,
                follower_max=follower_max,
            )

        total = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for query in queries:
                page_token: str | None = None
                for _ in range(max(1, pages)):
                    search_payload = {
                        "part": "snippet",
                        "q": query,
                        "type": "channel",
                        "maxResults": 25,
                        "key": self.settings.youtube_api_key,
                    }
                    if page_token:
                        search_payload["pageToken"] = page_token

                    search_resp = await client.get(f"{self.base_url}/search", params=search_payload)
                    search_resp.raise_for_status()
                    search_data = search_resp.json()

                    channel_ids = [it["snippet"]["channelId"] for it in search_data.get("items", [])]
                    if not channel_ids:
                        break

                    channel_resp = await client.get(
                        f"{self.base_url}/channels",
                        params={
                            "part": "snippet,statistics",
                            "id": ",".join(channel_ids),
                            "key": self.settings.youtube_api_key,
                            "maxResults": 50,
                        },
                    )
                    channel_resp.raise_for_status()
                    channels = channel_resp.json().get("items", [])

                    for channel in channels:
                        channel_id = channel.get("id")
                        if not channel_id or channel_id in dedup_ids:
                            continue

                        snippet = channel.get("snippet", {})
                        stats = channel.get("statistics", {})
                        follower_count = int(stats.get("subscriberCount", 0) or 0)
                        if follower_min is not None and follower_count < follower_min:
                            continue
                        if follower_max is not None and follower_count > follower_max:
                            continue

                        description = snippet.get("description", "")
                        email_match = EMAIL_RE.search(description)
                        custom_url = snippet.get("customUrl")
                        profile_url = (
                            f"https://www.youtube.com/{custom_url}"
                            if custom_url
                            else f"https://www.youtube.com/channel/{channel_id}"
                        )

                        db.add(
                            SearchResultRaw(
                                task_id=task_id,
                                platform="youtube",
                                platform_user_id=channel_id,
                                display_name=snippet.get("title", ""),
                                profile_url=profile_url,
                                follower_count=follower_count,
                                email=email_match.group(0) if email_match else None,
                                extra={"description": description, "query_used": query},
                            )
                        )
                        dedup_ids.add(channel_id)
                        total += 1

                    page_token = search_data.get("nextPageToken")
                    if not page_token:
                        break

        return total

    async def _mock_results(
        self,
        db: AsyncSession,
        task_id: str,
        query: str,
        follower_min: int | None = None,
        follower_max: int | None = None,
    ) -> int:
        samples: list[dict[str, Any]] = [
            {
                "platform_user_id": "mock-channel-1",
                "display_name": f"{query.title()} Creator",
                "profile_url": "https://www.youtube.com/@mockcreator",
                "follower_count": 45000,
                "email": "creator@example.com",
            },
            {
                "platform_user_id": "mock-channel-2",
                "display_name": f"{query.title()} Studio",
                "profile_url": "https://www.youtube.com/@mockstudio",
                "follower_count": 120000,
                "email": None,
            },
        ]

        filtered_samples = []
        for sample in samples:
            follower_count = sample["follower_count"]
            if follower_min is not None and follower_count < follower_min:
                continue
            if follower_max is not None and follower_count > follower_max:
                continue
            filtered_samples.append(sample)

        for sample in filtered_samples:
            db.add(
                SearchResultRaw(
                    task_id=task_id,
                    platform="youtube",
                    platform_user_id=sample["platform_user_id"],
                    display_name=sample["display_name"],
                    profile_url=sample["profile_url"],
                    follower_count=sample["follower_count"],
                    email=sample["email"],
                    extra={"mocked": True},
                )
            )
        return len(filtered_samples)
