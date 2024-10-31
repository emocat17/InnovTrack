from pydantic import BaseModel

class DocumentResponse(BaseModel):
    content: str
