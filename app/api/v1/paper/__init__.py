from fastapi import APIRouter
from .paper import router 

paper_router = APIRouter()

paper_router.include_router(router, tags=["爬取论文"])

__all__ = ["paper_router"]

