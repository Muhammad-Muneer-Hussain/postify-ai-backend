# 🚀 Postify AI Backend

---

## 🚀 Features (AI Modules)

* **AI Auto-Reply:** Social media comments par context-aware automatic replies.
* **AI Metadata Generator:** Video transcript se SEO-optimized Titles, Descriptions, aur Tags.
* **AI Post Generator:** Topic aur platform ke hisaab se text post aur AI-generated image.
* **AI Improvement Engine:** Video stats (Views, CTR, Watch time) analyze kar ke actionable suggestions.
* **AI Video Generator (Text-to-Video):** User ke prompt se script, images, human voiceover (Edge-TTS) aur captions mila kar MP4 video (*Background Job system*).
* **AI Thumbnail & Caption Generator:** Video ka frame analyze kar ke (Gemini Vision) clickbait thumbnail aur caption/hashtags generate karna.
* **AI Video Translator:** Video ko transcribe (Groq Whisper) kar ke dosri languages mein translate aur dub (Voiceover) karna.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **AI / LLMs:** Groq (Llama 3.1), Google Gemini (1.5 Flash)
* **Orchestration:** LangChain
* **Media Processing:** MoviePy, OpenCV, Pillow (PIL)
* **Text-to-Speech:** Edge-TTS (Human-like voices)
* **Image Generation:** Pollinations.ai (Free)
* **Server:** Uvicorn

---

## 📂 Folder Structure

```text
postify_ai_backend/
│
├── main.py                 # FastAPI app entry point & router configurations
├── requirements.txt        # Python dependencies
├── .env                    # API Keys (Groq, Gemini) - Not in Git
├── .gitignore
│
├── api/                    # API Routes (Endpoints for Web team)
│   ├── routes_reply.py
│   ├── routes_metadata.py
│   ├── routes_post.py
│   ├── routes_improvement.py
│   ├── routes_video.py
│   ├── routes_thumbnail.py
│   └── routes_translate.py
│
├── core/                   # Core AI logic
│   ├── llm_setup.py        # LLM initialization (Groq/Gemini)
│   └── prompts.py          # All prompt templates
│
├── schemas/                # Pydantic models (Request/Response validation)
│   ├── reply_schema.py
│   ├── metadata_schema.py
│   └── ... (other schemas)
│
├── images/                 # Auto-generated images/thumbnails (Git ignored)
└── videos/                 # Auto-generated/translated videos (Git ignored)
```

---

## ⚙️ Setup & Installation (Local Development)

### 1. Prerequisites
* Python 3.10+
* **FFmpeg** installed on your system (for video processing)

### 2. Get Free API Keys
* **Groq API Key:** Get from Groq Console
* **Gemini API Key:** Get from Google AI Studio

### 3. Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/postify-project/postify-ai-backend.git>
   cd postify_ai_backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the root directory and add your keys:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### 4. Run the Server
```bash
uvicorn main:app --reload
```
Server start ho jayega aur `http://localhost:8000` par chalega.

---

## 📚 API Documentation

Jab server chal raha ho, toh browser mein is link par jayen:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

Yahan FastAPI automatically **Swagger UI** generate karta hai jahan Web Team saari endpoints test kar sakti hai.

### Key Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/ai/reply/` | Generate auto-reply |
| `POST` | `/api/ai/metadata/` | Generate video metadata |
| `POST` | `/api/ai/post/` | Generate post with image |
| `POST` | `/api/ai/improve/` | Get video improvement suggestions |
| `POST` | `/api/ai/video/` | Start video generation (*Returns Job ID*) |
| `GET` | `/api/ai/video/status/{job_id}` | Check video generation status |
| `POST` | `/api/ai/thumbnail/` | Start thumbnail generation (*Returns Job ID*) |
| `GET` | `/api/ai/thumbnail/status/{job_id}` | Check thumbnail status |
| `POST` | `/api/ai/translate/` | Start video translation (*Returns Job ID*) |
| `GET` | `/api/ai/translate/status/{job_id}` | Check translation status |