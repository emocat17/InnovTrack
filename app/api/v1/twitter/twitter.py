# app/api/v1/twitter/twitter.py
from fastapi import APIRouter, BackgroundTasks
from app.controllers.twitter_scraper import twitter_scraper
from app.schemas.twitter_schema import RunTwitterScraperRequest
from app.schemas import Success # Assuming you have a generic Success response model

router = APIRouter()

@router.post("/run_scraper", summary="Run Twitter Scraper and Download Data")
async def run_twitter_scraper_endpoint(
    request_params: RunTwitterScraperRequest,
    background_tasks: BackgroundTasks # To run the potentially long task in the background
):
    """
    Initiates the Twitter scraping process based on the provided parameters.
    The process runs in the background, and results will be saved to the server.
    """
    # Add the potentially long-running task to background tasks
    # The twitter_scraper.run_scraper method itself uses run_in_executor
    # so it won't block the main thread that background_tasks uses for scheduling.
    background_tasks.add_task(twitter_scraper.run_scraper, request_params)
    
    # Return an immediate response
    return Success(msg=f"Twitter scraping task for '{request_params.keyword}' has been initiated in the background. Check server logs for progress.")