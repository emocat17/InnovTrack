# app/api/v1/WIPO_spider/__init__.py
from fastapi import APIRouter
from .WIPO_spider import router

WIPO_spider_router = APIRouter()
WIPO_spider_router.include_router(router, tags=["WIPO爬虫"])

__all__ = ["WIPO_spider_router"]
