from fastapi import APIRouter
from .v1 import v1_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")



from .v1.document import document_router  # demo
api_router.include_router(document_router, prefix="/v1") #demo

#论文爬虫路由
from .v1.arxiv_spider import arxiv_router
api_router.include_router(arxiv_router,prefix="/v1") 

#论文获取本地数据库路由
from .v1.arxiv_database import arxiv_database_router
api_router.include_router(arxiv_database_router,prefix="/v1")

from .v1.WIPO_spider import WIPO_spider_router
api_router.include_router(WIPO_spider_router,prefix="/v1")

__all__ = ["api_router"]