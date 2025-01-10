from fastapi import APIRouter ,BackgroundTasks #BackgroundTasks为后台任务,防止超时
from app.controllers.WIPO_spider import WIPO_spider
from app.schemas import Success
from app.schemas.WIPOschema import FetchWIPORequest

router = APIRouter()

@router.post("/fetch_WIPO",summary="爬取WIPO专利")

async def fetch_WIPO(request: FetchWIPORequest):  # 接收请求体
    data = await WIPO_spider.fetch_WIPO_data(request.keyword)  # 使用 request.keyword
    return Success(data=data)

