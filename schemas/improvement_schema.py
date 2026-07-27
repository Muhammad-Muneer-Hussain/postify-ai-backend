from pydantic import BaseModel
from typing import List

class VideoStatsRequest(BaseModel):
    video_title: str
    views: int
    avg_watch_time_percentage: float  # e.g., 45.5 (means 45.5%)
    click_through_rate: float         # e.g., 3.2 (means 3.2%)
    likes: int
    comments: int

class ImprovementResponse(BaseModel):
    performance_analysis: str       
    identified_issues: List[str]    
    actionable_suggestions: List[str] 