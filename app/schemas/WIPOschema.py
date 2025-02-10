from pydantic import BaseModel

class FetchWIPORequest(BaseModel):
    keyword: str

class DatabaseKeywordRequest(BaseModel):#实际没用到 仅做测试
    keyword: str
