from pydantic import BaseModel
from typing import List, Optional

class PostRequest(BaseModel):
    topic: str
    platform: str
    tone: str = "Professional"

class PostResponse(BaseModel):
    caption: str
    hashtags: List[str]
    call_to_action: str
    image_prompt: str
    image_url: Optional[str] = None

# Naya: Job ID ka response
class PostJobResponse(BaseModel):
    job_id: str
    status: str

# Naya: Status check karne ka response
class PostStatusResponse(BaseModel):
    status: str
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None