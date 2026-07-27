import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Cloudary Configuration
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

def upload_media(file_path, resource_type="image"):
    """Yeh function file ko cloudinary par upload kar ke uska URL return karega."""
    try:
        response = cloudinary.uploader.upload(file_path, resource_type=resource_type)
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
        return None