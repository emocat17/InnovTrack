# app/api/v1/twitter/__init__.py
from fastapi import APIRouter
from .twitter import router 

twitter_router = APIRouter()
# No prefix here, it will be defined in app/api/v1/__init__.py
twitter_router.include_router(router, tags=["Twitter Scraper"]) 

__all__ = ["twitter_router"]