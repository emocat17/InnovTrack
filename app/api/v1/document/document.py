from fastapi import APIRouter
from app.controllers.document import document_controller
from app.schemas.document import DocumentResponse

router = APIRouter()

@router.get("/fetch", response_model=DocumentResponse, summary="获取爬虫数据")
async def fetch_document_data():
    return await document_controller.fetch_data()
