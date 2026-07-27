from pydantic import BaseModel

class ReplyRequest(BaseModel):
    platform: str
    comment: str
    context: str

class ReplyResponse(BaseModel):
    suggested_reply: str
    sentiment: str