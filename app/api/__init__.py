from fastapi import APIRouter
from .v1 import v1_router

# #这边是自己加的
from .v1.document import document_router  # 新增
# #end

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")
# #
api_router.include_router(document_router, prefix="/v1")
# #


__all__ = ["api_router"]
