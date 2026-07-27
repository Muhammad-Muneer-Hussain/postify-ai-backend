from pydantic import BaseModel
from typing import List, Optional

class ThumbRequest(BaseModel):
    video_url: str

class ThumbResponse(BaseModel):
    caption: str
    hashtags: List[str]
    thumbnail_url: str
    thumbnail_text: str   
    image_prompt: str     

class ThumbJobResponse(BaseModel):
    job_id: str
    status: str

class ThumbStatusResponse(BaseModel):
    status: str
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    error: Optional[str] = None