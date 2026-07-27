from fastapi import APIRouter, BackgroundTasks
from schemas.thumbnail_schema import ThumbRequest, ThumbJobResponse, ThumbStatusResponse, ThumbResponse
from core.llm_setup import get_vision_llm
from core.prompts import THUMB_PROMPT
from core.cloudinary_setup import upload_media 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage
import cv2
import requests
import urllib.parse
import uuid
import os
import base64
from PIL import Image, ImageDraw, ImageFont

router = APIRouter()
thumb_jobs = {}

def process_thumb_job(job_id: str, video_url: str):
    try:
        thumb_jobs[job_id]["status"] = "Downloading Video..."
        video_filename = f"temp_vid_{job_id}.mp4"
        response = requests.get(video_url)
        with open(video_filename, 'wb') as f:
            f.write(response.content)

        thumb_jobs[job_id]["status"] = "Analyzing Video Frame..."
        cap = cv2.VideoCapture(video_filename)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
        ret, frame = cap.read()
        cap.release()
        
        frame_filename = f"temp_frame_{job_id}.jpg"
        cv2.imwrite(frame_filename, frame)
        
        llm = get_vision_llm()
        parser = JsonOutputParser(pydantic_object=ThumbResponse)
        
        with open(frame_filename, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
        message = HumanMessage(
            content=[
                {"type": "text", "text": THUMB_PROMPT.format(format_instructions=parser.get_format_instructions())},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        )
        
        ai_response = llm.invoke([message])
        parsed_data = parser.parse(ai_response.content)
        
        thumb_text = parsed_data.get("thumbnail_text", "Awesome Video!")
        caption = parsed_data.get("caption", "")
        hashtags = parsed_data.get("hashtags", [])
        
        thumb_jobs[job_id]["status"] = "Generating Thumbnail..."
        img_prompt = parsed_data.get("image_prompt", "Eye-catching YouTube thumbnail background, highly detailed, vibrant colors")
        encoded_prompt = urllib.parse.quote(img_prompt)
        
        import random
        seed = random.randint(1, 1000000)
        bg_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={seed}"
        bg_data = requests.get(bg_url).content
        thumb_path = f"temp_thumb_{job_id}.jpg"
        with open(thumb_path, 'wb') as f:
            f.write(bg_data)
        
        img = Image.open(thumb_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()
            
        text_bbox = draw.textbbox((0, 0), thumb_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (img.width - text_width) / 2
        y = img.height - text_height - 100
        
        for adj in [-2, 2]:
            draw.text((x+adj, y), thumb_text, fill="black", font=font)
            draw.text((x, y+adj), thumb_text, fill="black", font=font)
        draw.text((x, y), thumb_text, fill="yellow", font=font)
        
        # Temp final file
        final_thumb_path = f"temp_final_thumb_{job_id}.jpg"
        img.save(final_thumb_path, "JPEG")
        
        # 6. Delete Temp files
        if os.path.exists(video_filename): os.remove(video_filename)
        if os.path.exists(frame_filename): os.remove(frame_filename)
        if os.path.exists(thumb_path): os.remove(thumb_path)
        
        # 7. Cloudinary upload
        thumb_jobs[job_id]["status"] = "Uploading to Cloud..."
        cloud_thumb_url = upload_media(final_thumb_path, resource_type="image")
        if os.path.exists(final_thumb_path): os.remove(final_thumb_path)
        
        thumb_jobs[job_id] = {
            "status": "completed",
            "caption": caption,
            "hashtags": hashtags,
            "thumbnail_url": cloud_thumb_url,
            "error": None
        }
        
    except Exception as e:
        thumb_jobs[job_id] = {
            "status": "failed",
            "caption": None,
            "hashtags": None,
            "thumbnail_url": None,
            "error": str(e)
        }

@router.post("/", response_model=ThumbJobResponse)
async def start_thumb_generation(request: ThumbRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    thumb_jobs[job_id] = {"status": "queued", "caption": "", "hashtags": [], "thumbnail_url": "", "error": None}
    background_tasks.add_task(process_thumb_job, job_id, request.video_url)
    return ThumbJobResponse(job_id=job_id, status="queued")

@router.get("/status/{job_id}", response_model=ThumbStatusResponse)
def get_thumb_status(job_id: str):
    if job_id in thumb_jobs:
        job = thumb_jobs[job_id]
        return ThumbStatusResponse(
            status=job["status"],
            caption=job["caption"],
            hashtags=job["hashtags"],
            thumbnail_url=job["thumbnail_url"],
            error=job["error"]
        )
    return ThumbStatusResponse(status="not_found")