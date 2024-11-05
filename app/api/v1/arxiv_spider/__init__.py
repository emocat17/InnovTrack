# app/api/v1/arxiv/__init__.py
from fastapi import APIRouter
from .arxiv import router

arxiv_router = APIRouter()
arxiv_router.include_router(router, tags=["arxiv爬虫"])

__all__ = ["arxiv_router"]
