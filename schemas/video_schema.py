from pydantic import BaseModel
from typing import List, Optional


class VideoScene(BaseModel):
    visuals: str
    voiceover: str

class VideoScriptResponse(BaseModel):
    scenes: List[VideoScene]


class VideoGenRequest(BaseModel):
    prompt: str
    captions: bool = False 

class VideoJobResponse(BaseModel):
    job_id: str
    status: str


class VideoStatusResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    script: Optional[str] = None
    error: Optional[str] = None