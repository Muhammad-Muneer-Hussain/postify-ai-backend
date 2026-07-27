from pydantic import BaseModel
from typing import List

class MetadataRequest(BaseModel):
    video_transcript: str 
    platform: str = "YouTube"
    
class MetadataResponse(BaseModel):
    title: str
    description: str
    tags: List[str]