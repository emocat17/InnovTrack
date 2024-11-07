# app/api/v1/arxiv_database/arxiv_database.py
from fastapi import APIRouter
from app.controllers.arxiv_database import get_arxiv_database
from app.schemas import Success

router = APIRouter()

@router.get("/get_arxiv_database", summary="获取论文数据")
async def get_paper_data(keyword: str):
    try:
        # 调用实际的读取方法
        data = await get_arxiv_database.read_paper_data(keyword)
        return Success(data=data)
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": "服务器错误，请稍后再试。"}
