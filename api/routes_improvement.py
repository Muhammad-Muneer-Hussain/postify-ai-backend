from fastapi import APIRouter
from schemas.improvement_schema import VideoStatsRequest, ImprovementResponse
from core.llm_setup import get_llm
from core.prompts import IMPROVEMENT_PROMPT
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter()

@router.post("/", response_model=ImprovementResponse)
async def generate_improvements(request: VideoStatsRequest):
    llm = get_llm()
    
    # JSON Parser setup
    parser = JsonOutputParser(pydantic_object=ImprovementResponse)
    
    # AI chain 
    chain = IMPROVEMENT_PROMPT | llm | parser
    
    # AI invoke k
    response = chain.invoke({
        "video_title": request.video_title,
        "views": request.views,
        "watch_time": request.avg_watch_time_percentage,
        "ctr": request.click_through_rate,
        "likes": request.likes,
        "comments": request.comments,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Return Response 
    return ImprovementResponse(
        performance_analysis=response.get("performance_analysis", ""),
        identified_issues=response.get("identified_issues", []),
        actionable_suggestions=response.get("actionable_suggestions", [])
    )