from fastapi import APIRouter
from .v1 import v1_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")




from .v1.document import document_router  # 新增
api_router.include_router(document_router, prefix="/v1") #新增

#论文爬虫
from .v1.arxiv import arxiv_router
api_router.include_router(arxiv_router,prefix="/v1") 



__all__ = ["api_router"]