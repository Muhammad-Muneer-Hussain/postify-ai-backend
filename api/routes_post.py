from fastapi import APIRouter, BackgroundTasks
from schemas.post_schema import PostRequest, PostResponse, PostJobResponse, PostStatusResponse
from core.llm_setup import get_llm
from core.prompts import POST_PROMPT
from core.cloudinary_setup import upload_media
from langchain_core.output_parsers import JsonOutputParser
import urllib.parse
import requests 
import uuid 
import os

router = APIRouter()

# In-memory dictionary save job status
post_jobs = {}

def process_post_job(job_id: str, topic: str, platform: str, tone: str):
    try:
        post_jobs[job_id]["status"] = "Generating Content..."
        llm = get_llm()
        
        parser = JsonOutputParser(pydantic_object=PostResponse)
        chain = POST_PROMPT | llm | parser
        
        response = chain.invoke({
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "format_instructions": parser.get_format_instructions()
        })
        
        img_prompt = response.get("image_prompt", topic)
        
        post_jobs[job_id]["status"] = "Generating Image..."
        encoded_prompt = urllib.parse.quote(img_prompt)
        external_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
        
        cloud_url = None
        try:
            img_data = requests.get(external_image_url).content
            temp_filepath = f"temp_post_{job_id}.jpg"
            
            with open(temp_filepath, 'wb') as f:
                f.write(img_data)
                
            post_jobs[job_id]["status"] = "Uploading to Cloud..."
            cloud_url = upload_media(temp_filepath, resource_type="image")
            
            if os.path.exists(temp_filepath): os.remove(temp_filepath)
            
        except Exception as e:
            print(f"Image processing error: {e}")
            cloud_url = None
        
        post_jobs[job_id] = {
            "status": "completed",
            "caption": response.get("caption", ""),
            "hashtags": response.get("hashtags", []),
            "call_to_action": response.get("call_to_action", ""),
            "image_prompt": img_prompt,
            "image_url": cloud_url,
            "error": None
        }
        
    except Exception as e:
        post_jobs[job_id] = {
            "status": "failed",
            "caption": None,
            "hashtags": None,
            "call_to_action": None,
            "image_prompt": None,
            "image_url": None,
            "error": str(e)
        }

# Endpoint 1: Post generation and return job id
@router.post("/", response_model=PostJobResponse)
async def start_post_generation(request: PostRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    post_jobs[job_id] = {"status": "queued", "caption": "", "hashtags": [], "call_to_action": "", "image_prompt": "", "image_url": None, "error": None}
    
    background_tasks.add_task(process_post_job, job_id, request.topic, request.platform, request.tone)
    
    return PostJobResponse(job_id=job_id, status="queued")

# Endpoint 2: Job status check 
@router.get("/status/{job_id}", response_model=PostStatusResponse)
async def get_post_status(job_id: str):
    if job_id in post_jobs:
        job = post_jobs[job_id]
        return PostStatusResponse(
            status=job["status"],
            caption=job["caption"],
            hashtags=job["hashtags"],
            call_to_action=job["call_to_action"],
            image_prompt=job["image_prompt"],
            image_url=job["image_url"],
            error=job["error"]
        )
    return PostStatusResponse(status="not_found")