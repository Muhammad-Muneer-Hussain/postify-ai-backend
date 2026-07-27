from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    
    return ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

def get_vision_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.7,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )