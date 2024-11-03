from pydantic import BaseModel

class FetchArxivRequest(BaseModel):
    keyword: str
