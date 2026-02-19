import uuid

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.search_task import SearchTask
from app.services.search_service import SearchService


async def run_search_task(task_id: uuid.UUID) -> None:
    search_service = SearchService()
    async with AsyncSessionLocal() as session:
        task = (await session.execute(select(SearchTask).where(SearchTask.id == task_id))).scalar_one_or_none()
        if task is None:
            return

        try:
            await search_service.run_search_pipeline(session, task)
            await session.commit()
        except Exception:
            task.status = "failed"
            await session.commit()
            raise
