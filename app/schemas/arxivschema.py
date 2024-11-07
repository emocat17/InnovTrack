from pydantic import BaseModel

class FetchArxivRequest(BaseModel):
    keyword: str

class DatabaseKeywordRequest(BaseModel):#实际没用到 仅做测试
    keyword: str
