from fastapi import APIRouter
from app.controllers.document import document_controller
from app.schemas import Success

router = APIRouter()

@router.get("/fetch", summary="获取爬虫数据")
async def fetch_document_data():
    data =  await document_controller.fetch_data()
    return Success(data = data)
