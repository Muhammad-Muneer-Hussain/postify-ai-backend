from fastapi import APIRouter, BackgroundTasks
from schemas.video_schema import VideoGenRequest, VideoJobResponse, VideoStatusResponse, VideoScriptResponse
from core.llm_setup import get_llm
from core.prompts import VIDEO_SCRIPT_PROMPT
from core.cloudinary_setup import upload_media 
from langchain_core.output_parsers import JsonOutputParser
import urllib.parse
import requests
import uuid
import os
import asyncio
import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

router = APIRouter()
video_jobs = {}

def process_video_job(job_id: str, prompt: str, captions: bool):
    try:
        video_jobs[job_id]["status"] = "Generating Script..."
        llm = get_llm()
        parser = JsonOutputParser(pydantic_object=VideoScriptResponse)
        chain = VIDEO_SCRIPT_PROMPT | llm | parser
        
        response = chain.invoke({
            "prompt": prompt,
            "format_instructions": parser.get_format_instructions()
        })
        
        scenes = response.get("scenes", [])
        if not scenes:
            scenes = [{"visuals": prompt, "voiceover": prompt}]
            
        video_clips = []
        temp_files = []
        full_script_text = ""
        
        video_jobs[job_id]["status"] = "Generating Media (Audio & Images)..."
        
        for i, scene in enumerate(scenes):
            visual = scene.get("visuals", "")
            voice = scene.get("voiceover", "")
            full_script_text += voice + " "
            
            encoded_prompt = urllib.parse.quote(visual)
            img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"
            img_data = requests.get(img_url).content
            img_path = f"temp_img_{job_id}_{i}.jpg"
            with open(img_path, 'wb') as f:
                f.write(img_data)
            temp_files.append(img_path)
            
            audio_path = f"temp_audio_{job_id}_{i}.mp3"
            communicate = edge_tts.Communicate(voice, voice="en-US-AriaNeural")
            asyncio.run(communicate.save(audio_path))
            temp_files.append(audio_path)
            
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).with_duration(audio_clip.duration).with_audio(audio_clip)
            
            if captions:
                try:
                    txt_clip = TextClip(text=voice, font_size=40, color='white', bg_color='black', method='caption', size=(680, None))
                    txt_clip = txt_clip.with_duration(audio_clip.duration).with_position(('center', 'bottom'))
                    img_clip = CompositeVideoClip([img_clip, txt_clip])
                except Exception as e:
                    pass
            
            video_clips.append(img_clip)
            
        video_jobs[job_id]["status"] = "Rendering Final Video..."
        final_video = concatenate_videoclips(video_clips, method="compose")
        
    
        video_filepath = f"temp_final_vid_{job_id}.mp4"
        final_video.write_videofile(video_filepath, fps=24, codec='libx264', audio_codec='aac', logger=None)
        
        for clip in video_clips:
            clip.close()
        final_video.close()
        
        for file in temp_files:
            if os.path.exists(file): os.remove(file)
                
        # Cloudinary Upload
        video_jobs[job_id]["status"] = "Uploading to Cloud..."
        cloud_video_url = upload_media(video_filepath, resource_type="video")
        if os.path.exists(video_filepath): os.remove(video_filepath)
        
        video_jobs[job_id] = {
            "status": "completed",
            "video_url": cloud_video_url,
            "script": full_script_text.strip(),
            "error": None
        }
        
    except Exception as e:
        video_jobs[job_id] = {
            "status": "failed",
            "video_url": None,
            "script": None,
            "error": str(e)
        }

@router.post("/", response_model=VideoJobResponse)
async def start_video_generation(request: VideoGenRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    video_jobs[job_id] = {"status": "queued", "video_url": None, "script": "", "error": None}
    background_tasks.add_task(process_video_job, job_id, request.prompt, request.captions)
    return VideoJobResponse(job_id=job_id, status="queued")

@router.get("/status/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(job_id: str):
    if job_id in video_jobs:
        job = video_jobs[job_id]
        return VideoStatusResponse(
            status=job["status"],
            video_url=job["video_url"],
            script=job["script"],
            error=job["error"]
        )
    return VideoStatusResponse(status="not_found")