# app/schemas/twitter_schema.py
from pydantic import BaseModel, Field
from typing import Optional, List

class RunTwitterScraperRequest(BaseModel):
    keyword: str = Field(..., description="Keyword for data storage folder name (e.g., 'AIResearch') and for subfolder naming if tag/filter are empty.")
    
    # Search parameters (mirroring those in initiate_twitter_download)
    tag: Optional[str] = Field(None, description="Main #tag to search (e.g., '#ZeroTrust')")
    search_all_these_words: Optional[str] = Field(None, description="e.g., 'what is happening'")
    search_exact_phrase: Optional[str] = Field(None, description="e.g., 'happy hour'")
    search_any_of_these_keywords: Optional[str] = Field(None, description="e.g., 'cats dogs'")
    search_none_of_these_words: Optional[str] = Field(None, description="e.g., 'fruit salad'")
    search_hashtags: Optional[List[str]] = Field(None, description="e.g., ['#Tech', '#AI']")
    search_from_user: Optional[str] = Field(None, description="Twitter username without '@', e.g., 'elonmusk'")
    search_filter_links: bool = Field(True, description="Add 'filter:links' to query. Usually True for media, False for text.")
    search_exclude_replies: bool = Field(True, description="Add '-filter:replies' to query.")
    search_until_date: Optional[str] = Field(None, description="YYYY-MM-DD, e.g., '2024-12-31'")
    search_since_date: Optional[str] = Field(None, description="YYYY-MM-DD, e.g., '2024-01-01'")
    
    # Operational parameters
    down_count: int = Field(100, description="Number of tweets to attempt to download.") # Default to a smaller number
    media_latest: bool = Field(True, description="True for 'Latest' tab, False for 'Media' tab (if not text_down).")
    text_down: bool = Field(False, description="True to download text only, False for media.")
    max_concurrent_requests: int = Field(2, description="Max concurrent media download requests.")

    class Config:
        schema_extra = {
            "example": {
                "keyword": "AIResearch",
                "tag": "#ArtificialIntelligence",
                "search_since_date": "2024-01-01",
                "search_until_date": "2024-01-10",
                "down_count": 50,
                "media_latest": True,
                "text_down": False
            }
        }