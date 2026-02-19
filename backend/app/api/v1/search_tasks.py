import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_user_id
from app.models.search_result import SearchResultDeduped, SearchResultRaw
from app.models.search_task import SearchTask
from app.schemas.search_task import (
    SearchResultResponse,
    SearchTaskCreate,
    SearchTaskCreateResponse,
    SearchTaskListItem,
    SearchTaskStatusResponse,
)
from app.services.search_service import SearchService
from app.workers.tasks import run_search_task

router = APIRouter()


@router.post("/search-tasks", response_model=SearchTaskCreateResponse)
async def create_search_task(
    body: SearchTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> SearchTaskCreateResponse:
    service = SearchService()
    parsed = service.parse_query(body.model_dump())

    task = SearchTask(user_id=user_id, query_raw=body.query, query_parsed=parsed, status="pending")
    db.add(task)
    await db.commit()
    await db.refresh(task)

    background_tasks.add_task(run_search_task, task.id)
    return SearchTaskCreateResponse(task_id=task.id, status=task.status)


@router.get("/search-tasks/{task_id}", response_model=SearchTaskStatusResponse)
async def get_search_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SearchTaskStatusResponse:
    task = (await db.execute(select(SearchTask).where(SearchTask.id == task_id))).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")

    return SearchTaskStatusResponse(
        task_id=task.id,
        status=task.status,
        result_count=task.result_count,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/search-tasks", response_model=list[SearchTaskListItem])
async def list_search_tasks(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> list[SearchTaskListItem]:
    tasks = (
        await db.execute(
            select(SearchTask)
            .where(SearchTask.user_id == user_id)
            .order_by(SearchTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    return [
        SearchTaskListItem(
            task_id=task.id,
            query_raw=task.query_raw,
            status=task.status,
            result_count=task.result_count,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@router.get("/search-tasks/{task_id}/results", response_model=list[SearchResultResponse])
async def get_search_task_results(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> list[SearchResultResponse]:
    rows = (
        await db.execute(
            select(SearchResultDeduped, SearchResultRaw)
            .join(SearchResultRaw, SearchResultRaw.id == SearchResultDeduped.raw_result_id)
            .where(SearchResultDeduped.task_id == task_id)
            .order_by(SearchResultDeduped.created_at.asc())
        )
    ).all()

    results: list[SearchResultResponse] = []
    for deduped, raw in rows:
        results.append(
            SearchResultResponse(
                deduped_id=deduped.id,
                raw_result_id=raw.id,
                dedup_status=deduped.dedup_status,
                matched_influencer_id=deduped.matched_influencer_id,
                platform=raw.platform,
                platform_user_id=raw.platform_user_id,
                display_name=raw.display_name,
                profile_url=raw.profile_url,
                follower_count=raw.follower_count,
                email=raw.email,
            )
        )
    return results
