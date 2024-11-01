from fastapi import APIRouter
from .document import router

document_router = APIRouter()
#document_router.include_router(router, prefix="/document", tags=["测试"])
document_router.include_router(router, tags=["测试"])
#此处内容在 系统管理/API管理  点击刷新后  会更新到页面上

__all__ = ["document_router"]
