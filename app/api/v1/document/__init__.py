from fastapi import APIRouter
from .document import router

document_router = APIRouter()
document_router.include_router(router, prefix="/document", tags=["Document Module"])

__all__ = ["document_router"]
