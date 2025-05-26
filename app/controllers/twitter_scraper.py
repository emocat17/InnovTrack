# app/controllers/twitter_scraper.py
import os
import asyncio
import threading # For running the blocking script
from app.controllers.twitter_download import tag_down_logic # Actual scraping logic
from app.schemas.twitter_schema import RunTwitterScraperRequest

class TwitterScraper:
    @staticmethod
    def run_scraper_sync(params: RunTwitterScraperRequest): # Synchronous wrapper
        # 1. Define base data directory (relative to project root)
        # Assuming project root is parent of 'app' and 'Data'
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base_data_dir = os.path.join(project_root, "Data")

        if not os.path.exists(base_data_dir):
            os.makedirs(base_data_dir, exist_ok=True)

        # 2. Define specific output directory structure: Data/{keyword}/socialmedia/twitter/tag/
        # The tag_down_logic will create a further subfolder inside this path based on the query.
        keyword_path_segment = tag_down_logic.clean_filename_for_paths(params.keyword) # Sanitize keyword for path
        output_directory_for_logic = os.path.join(base_data_dir, keyword_path_segment, "socialmedia", "twitter", "tag")
        
        if not os.path.exists(output_directory_for_logic):
            os.makedirs(output_directory_for_logic, exist_ok=True)
        
        print(f"Controller: Output directory for twitter_download logic: {output_directory_for_logic}")

        try:
            tag_down_logic.initiate_twitter_download(
                base_output_directory=output_directory_for_logic,
                keyword_for_foldername=params.keyword, # Pass the original keyword for naming logic
                p_tag=params.tag,
                p_search_all_these_words=params.search_all_these_words,
                p_search_exact_phrase=params.search_exact_phrase,
                p_search_any_of_these_keywords=params.search_any_of_these_keywords,
                p_search_none_of_these_words=params.search_none_of_these_words,
                p_search_hashtags=params.search_hashtags,
                p_search_from_user=params.search_from_user,
                p_search_filter_links=params.search_filter_links,
                p_search_exclude_replies=params.search_exclude_replies,
                p_search_until_date=params.search_until_date,
                p_search_since_date=params.search_since_date,
                p_down_count=params.down_count,
                p_media_latest=params.media_latest,
                p_text_down=params.text_down,
                p_max_concurrent_requests=params.max_concurrent_requests
            )
            return f"Twitter data download process for '{params.keyword}' completed. Check logs and '{output_directory_for_logic}'."
        except Exception as e:
            print(f"Error in TwitterScraper calling tag_down_logic: {e}")
            import traceback
            traceback.print_exc()
            return f"Twitter data download process for '{params.keyword}' failed. Error: {e}"

    @staticmethod
    async def run_scraper(params: RunTwitterScraperRequest):
        # Run the synchronous, blocking function in a separate thread
        # to avoid blocking the FastAPI event loop.
        loop = asyncio.get_event_loop()
        # Using default executor (ThreadPoolExecutor)
        result_message = await loop.run_in_executor(
            None, 
            TwitterScraper.run_scraper_sync, 
            params
        )
        return result_message

twitter_scraper = TwitterScraper()