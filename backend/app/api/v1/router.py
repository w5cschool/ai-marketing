from fastapi import APIRouter

from app.api.v1 import campaigns, email_drafts, influencers, search_tasks

api_router = APIRouter()
api_router.include_router(search_tasks.router, tags=["search-tasks"])
api_router.include_router(influencers.router, tags=["influencers"])
api_router.include_router(email_drafts.router, tags=["email-drafts"])
api_router.include_router(campaigns.router, tags=["campaigns"])
