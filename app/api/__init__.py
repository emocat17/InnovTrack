from fastapi import APIRouter

from .v1 import v1_router
# ###
from .v1.document import document_router  # demo
from .v1.arxiv_spider import arxiv_router
from .v1.arxiv_database import arxiv_database_router
from .v1.WIPO_spider import WIPO_spider_router
from .v1.twitter import twitter_router as new_twitter_scraper_api_router 


api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")

# demo
api_router.include_router(document_router, prefix="/v1") #demo

# 论文爬虫路由

api_router.include_router(arxiv_router,prefix="/v1") 

# 论文获取本地数据库路由
api_router.include_router(arxiv_database_router,prefix="/v1")

api_router.include_router(WIPO_spider_router,prefix="/v1")

api_router.include_router(v1_router, prefix="/v1") 

__all__ = ["api_router"]
