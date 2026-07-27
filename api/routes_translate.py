from fastapi import APIRouter, BackgroundTasks
from schemas.translate_schema import TranslateRequest, TranslateJobResponse, TranslateStatusResponse
from core.llm_setup import get_llm
from core.prompts import TRANSLATE_PROMPT
from core.cloudinary_setup import upload_media 
import requests
import uuid
import os
import edge_tts
import asyncio
from moviepy import VideoFileClip, AudioFileClip
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
translate_jobs = {}

TTS_VOICES = {
    "spanish": "es-ES-HelenaNeural",
    "urdu": "ur-PK-UzmaNeural",
    "french": "fr-FR-DeniseNeural",
    "hindi": "hi-IN-SwaraNeural",
    "arabic": "ar-SA-HamedNeural",
    "english": "en-US-AriaNeural"
}

def process_translation_job(job_id: str, video_url: str, target_language: str):
    try:
        video_filename = f"temp_trans_vid_{job_id}.mp4"
        audio_filename = f"temp_trans_audio_{job_id}.mp3"
        new_audio_filename = f"temp_trans_new_audio_{job_id}.mp3"
        
        translate_jobs[job_id]["status"] = "Downloading Video..."
        response = requests.get(video_url)
        with open(video_filename, 'wb') as f:
            f.write(response.content)
            
        translate_jobs[job_id]["status"] = "Extracting Audio..."
        video_clip = VideoFileClip(video_filename)
        video_clip.audio.write_audiofile(audio_filename, logger=None)
        
        translate_jobs[job_id]["status"] = "Transcribing Audio (Whisper)..."
        with open(audio_filename, 'rb') as f:
            whisper_response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
                files={"file": f},
                data={"model": "whisper-large-v3"}
            )
        original_text = whisper_response.json().get("text", "")
        
        translate_jobs[job_id]["status"] = f"Translating to {target_language}..."
        llm = get_llm()
        chain = TRANSLATE_PROMPT | llm
        translated_text = chain.invoke({"text": original_text, "target_language": target_language}).content
        
        translate_jobs[job_id]["status"] = "Generating New Voiceover..."
        voice = TTS_VOICES.get(target_language.lower(), "en-US-AriaNeural")
        
        async def generate_tts():
            communicate = edge_tts.Communicate(translated_text, voice=voice)
            await communicate.save(new_audio_filename)
        asyncio.run(generate_tts())
        
        translate_jobs[job_id]["status"] = "Merging New Audio with Video..."
        new_audio_clip = AudioFileClip(new_audio_filename)
        
        if new_audio_clip.duration > video_clip.duration:
            new_audio_clip = new_audio_clip.subclipped(0, video_clip.duration)
            
        final_video = video_clip.with_audio(new_audio_clip)
        

        final_video_path = f"temp_final_trans_{job_id}.mp4"
        final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac', logger=None)
        
        video_clip.close()
        new_audio_clip.close()
        final_video.close()
        
        # delete temp file
        for f in [video_filename, audio_filename, new_audio_filename]:
            if os.path.exists(f): os.remove(f)
                
        # Cloudinary par upload karna
        translate_jobs[job_id]["status"] = "Uploading to Cloud..."
        cloud_trans_url = upload_media(final_video_path, resource_type="video")
        if os.path.exists(final_video_path): os.remove(final_video_path)
        
        translate_jobs[job_id] = {
            "status": "completed",
            "translated_video_url": cloud_trans_url,
            "original_text": original_text,
            "translated_text": translated_text,
            "error": None
        }
        
    except Exception as e:
        translate_jobs[job_id] = {
            "status": "failed",
            "translated_video_url": None,
            "original_text": None,
            "translated_text": None,
            "error": str(e)
        }

@router.post("/", response_model=TranslateJobResponse)
async def start_translation(request: TranslateRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    translate_jobs[job_id] = {"status": "queued", "translated_video_url": "", "original_text": "", "translated_text": "", "error": None}
    background_tasks.add_task(process_translation_job, job_id, request.video_url, request.target_language)
    return TranslateJobResponse(job_id=job_id, status="queued")

@router.get("/status/{job_id}", response_model=TranslateStatusResponse)
async def get_translation_status(job_id: str):
    if job_id in translate_jobs:
        job = translate_jobs[job_id]
        return TranslateStatusResponse(
            status=job["status"],
            translated_video_url=job["translated_video_url"],
            original_text=job["original_text"],
            translated_text=job["translated_text"],
            error=job["error"]
        )
    return TranslateStatusResponse(status="not_found")