import os
import cloudinary
import cloudinary.uploader
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_chunk_to_cloudinary(chunk_id: str, chunk_text: str) -> str:
    """
    Upload chunk text as a .txt file to Cloudinary.
    Returns public URL.
    """
  
    file_like = BytesIO(chunk_text.encode("utf-8"))

    result = cloudinary.uploader.upload(
        file_like,
        resource_type="raw",              # IMPORTANT for txt
        public_id=f"documents/{chunk_id}",   # folder in Cloudinary
        overwrite=True
    )

    return result["secure_url"]


