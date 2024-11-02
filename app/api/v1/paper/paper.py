
from fastapi import APIRouter
from app.controllers.spider.paper import paper_controller
from app.schemas import Success

router = APIRouter()

@router.post("/download-papers")
async def download_papers(keyword: str):
    data = await paper_controller.download_papers(keyword)
    return Success(data=data)

    #return await ArxivDownloaderController.download_papers(keyword)
