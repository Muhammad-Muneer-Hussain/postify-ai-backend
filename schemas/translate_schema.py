from pydantic import BaseModel
from typing import Optional

class TranslateRequest(BaseModel):
    video_url: str
    target_language: str 

class TranslateJobResponse(BaseModel):
    job_id: str
    status: str

class TranslateStatusResponse(BaseModel):
    status: str
    translated_video_url: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    error: Optional[str] = None