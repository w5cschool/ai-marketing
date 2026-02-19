import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.influencer import Influencer
from app.models.search_result import SearchResultDeduped, SearchResultRaw
from app.models.search_task import SearchTask
from app.services.dedup_service import compute_dedup_status
from app.services.youtube_connector import YouTubeConnector


class SearchService:
    def __init__(self) -> None:
        self.youtube = YouTubeConnector()

    def parse_query(self, payload: dict) -> dict:
        query_raw = (payload.get("query") or "").strip()
        normalized_query = query_raw.lower()

        follower_min = payload.get("follower_min")
        follower_max = payload.get("follower_max")
        if follower_min is None or follower_max is None:
            auto_min, auto_max = self._extract_follower_range(normalized_query)
            follower_min = follower_min if follower_min is not None else auto_min
            follower_max = follower_max if follower_max is not None else auto_max

        region = payload.get("region") or self._extract_region(normalized_query)
        search_queries = self._build_search_queries(query_raw, region)

        return {
            "platforms": payload.get("platforms", ["youtube"]),
            "region": region,
            "follower_min": follower_min,
            "follower_max": follower_max,
            "search_queries": search_queries,
        }

    async def run_search_pipeline(self, db: AsyncSession, task: SearchTask) -> int:
        task.status = "running"
        await db.flush()

        parsed = task.query_parsed or {}
        platforms = parsed.get("platforms") or ["youtube"]
        search_queries = parsed.get("search_queries") or [task.query_raw]
        follower_min = parsed.get("follower_min")
        follower_max = parsed.get("follower_max")

        if "youtube" in platforms:
            await self.youtube.fetch_and_store(
                db,
                task_id=str(task.id),
                queries=search_queries,
                follower_min=follower_min,
                follower_max=follower_max,
            )

        await db.flush()
        raw_rows = (
            await db.execute(select(SearchResultRaw).where(SearchResultRaw.task_id == task.id).order_by(SearchResultRaw.fetched_at.asc()))
        ).scalars().all()

        existing_influencers = (
            await db.execute(
                select(Influencer.id, Influencer.platform, Influencer.platform_user_id, Influencer.display_name, Influencer.profile_url, Influencer.follower_count, Influencer.email)
            )
        ).all()
        existing_dict = [dict(row._mapping) for row in existing_influencers]

        for raw in raw_rows:
            status, matched_id = compute_dedup_status(
                {
                    "platform": raw.platform,
                    "platform_user_id": raw.platform_user_id,
                    "display_name": raw.display_name,
                    "profile_url": raw.profile_url,
                    "follower_count": raw.follower_count,
                    "email": raw.email,
                },
                existing_dict,
            )

            db.add(
                SearchResultDeduped(
                    task_id=task.id,
                    raw_result_id=raw.id,
                    dedup_status=status,
                    matched_influencer_id=matched_id,
                )
            )

        task.result_count = len(raw_rows)
        task.status = "done"
        return len(raw_rows)

    def _extract_region(self, query: str) -> str | None:
        region_map = {
            "taiwan": "taiwan",
            "台灣": "taiwan",
            "台北": "taiwan",
            "usa": "usa",
            "united states": "usa",
            "us ": "usa",
            "uk": "uk",
            "united kingdom": "uk",
            "japan": "japan",
            "korea": "korea",
            "hong kong": "hong kong",
            "singapore": "singapore",
        }
        for key, value in region_map.items():
            if key in query:
                return value
        return None

    def _extract_follower_range(self, query: str) -> tuple[int | None, int | None]:
        between = re.search(r"between\s+(\d+[kKmM]?)\s+(?:and|to)\s+(\d+[kKmM]?)", query)
        if between:
            return self._parse_count(between.group(1)), self._parse_count(between.group(2))

        under = re.search(r"(?:less than|under|below|<=?)\s*(\d+[kKmM]?)", query)
        over = re.search(r"(?:more than|over|above|>=?)\s*(\d+[kKmM]?)", query)
        return (
            self._parse_count(over.group(1)) if over else None,
            self._parse_count(under.group(1)) if under else None,
        )

    def _parse_count(self, raw: str) -> int:
        text = raw.strip().lower()
        if text.endswith("k"):
            return int(float(text[:-1]) * 1000)
        if text.endswith("m"):
            return int(float(text[:-1]) * 1_000_000)
        return int(text)

    def _build_search_queries(self, query_raw: str, region: str | None) -> list[str]:
        q = query_raw.strip()
        q_no_constraints = re.sub(
            r"(find|less than|under|below|over|more than|above|between|followers?|subscribers?|which|who|with|than|\d+[kKmM]?)",
            " ",
            q,
            flags=re.IGNORECASE,
        )
        q_no_constraints = re.sub(r"\s+", " ", q_no_constraints).strip()

        base = q_no_constraints or q
        generic = "english youtube channel"
        if region:
            generic = f"{region} english youtube channel"

        # Keep only distinct, non-empty queries and limit API cost.
        ordered = [base, f"{base} channel", generic]
        unique: list[str] = []
        seen: set[str] = set()
        for item in ordered:
            item = item.strip()
            key = item.lower()
            if item and key not in seen:
                unique.append(item)
                seen.add(key)
        return unique[:3]
