# app/api/v1/arxiv/arxiv.py
from fastapi import APIRouter ,BackgroundTasks #BackgroundTasks为后台任务,防止超时
from app.controllers.arxiv_spider import arxiv_spider
from app.schemas import Success
from app.schemas.arxivschema import FetchArxivRequest

router = APIRouter()

@router.post("/fetch_arxiv",summary="爬取arxiv论文")

# async def fetch_arxiv(request: FetchArxivRequest):  # 接收请求体
#     data = await arxiv_spider.fetch_arxiv_data(request.keyword)  # 使用 request.keyword
#     return Success(data=data)

async def fetch_arxiv(request: FetchArxivRequest):  # 接收请求体
    data = await arxiv_spider.fetch_arxiv_data(request.keyword)  # 使用 request.keyword
    return Success(data=data)

