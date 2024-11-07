# app/api/v1/arxiv/__init__.py
from fastapi import APIRouter
from .arxiv_database import router

arxiv_database_router = APIRouter()
arxiv_database_router.include_router(router, tags=["arxiv论文数据库"])

__all__ = ["arxiv_database_router"]
