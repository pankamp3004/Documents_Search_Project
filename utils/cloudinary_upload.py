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


def chunk_to_html(chunk_text: str) -> str:
    escaped = (
        chunk_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    html = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>Chunk</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background: #111;
            color: #eee;
          }}
          pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
          }}
        </style>
      </head>
      <body>
        <h2>Document Chunk</h2>
        <pre>{escaped}</pre>
      </body>
    </html>
    """
    return html




def upload_chunk_to_cloudinary(chunk_id: str, chunk_text: str) -> str:
    """
    Upload chunk text as a .txt file to Cloudinary.
    Returns public URL.
    """
    html_text = chunk_to_html(chunk_text)
    file_like = BytesIO(html_text.encode("utf-8"))

    # file_like = BytesIO(chunk_text.encode("utf-8"))

    result = cloudinary.uploader.upload(
        file_like,
        resource_type="raw",              # IMPORTANT for txt
        # public_id=f"chunks/{chunk_id}",   # folder in Cloudinary
        public_id=f"chunks/{chunk_id}.html",   # ⭐ HTML
        overwrite=True
    )

    return result["secure_url"]


