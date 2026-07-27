import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import routes_reply, routes_metadata, routes_post, routes_improvement, routes_video, routes_thumbnail, routes_translate 

app = FastAPI(title="POSTIFY AI Backend", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs("images", exist_ok=True)
os.makedirs("videos", exist_ok=True)

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# Routers
app.include_router(routes_reply.router, prefix="/api/ai/reply", tags=["AI Auto-Reply"])
app.include_router(routes_metadata.router, prefix="/api/ai/metadata", tags=["AI Metadata Generator"])
app.include_router(routes_post.router, prefix="/api/ai/post", tags=["AI Post Generator"])
app.include_router(routes_improvement.router, prefix="/api/ai/improve", tags=["AI Improvement Engine"])
app.include_router(routes_video.router, prefix="/api/ai/video", tags=["AI Video Generator"])
app.include_router(routes_thumbnail.router, prefix="/api/ai/thumbnail", tags=["AI Thumbnail & Caption"])
app.include_router(routes_translate.router, prefix="/api/ai/translate", tags=["AI Video Translator"])

@app.get("/")
def read_root():
    return {"status": "QRYZON AI Backend is running successfully!"}