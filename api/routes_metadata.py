from fastapi import APIRouter
from schemas.metadata_schema import MetadataRequest, MetadataResponse
from core.llm_setup import get_llm
from core.prompts import METADATA_PROMPT
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter()

@router.post("/", response_model=MetadataResponse)
async def generate_metadata(request: MetadataRequest):
    llm = get_llm()
    
    # JSON Parser setup (AI returns its response in JSON formate)
    parser = JsonOutputParser(pydantic_object=MetadataResponse)
    
    # AI chain  (Prompt -> LLM -> Parser)
    chain = METADATA_PROMPT | llm | parser
    
    # AI invoke 
    response = chain.invoke({
        "transcript": request.video_transcript,
        "platform": request.platform,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Return Response 
    return MetadataResponse(
        title=response.get("title", ""),
        description=response.get("description", ""),
        tags=response.get("tags", [])
    )