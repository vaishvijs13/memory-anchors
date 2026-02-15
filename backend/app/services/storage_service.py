from __future__ import annotations

"""Supabase Storage service for file uploads."""

import uuid
from typing import Optional

from supabase import create_client, Client

from ..config import settings


_client: Optional[Client] = None


def get_storage_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment"
            )
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _client


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def get_content_type(filename: str) -> str:
    """Determine content type from filename."""
    ext = get_file_extension(filename)
    content_types = {
        # Images
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        # Videos
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
        # Audio
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
        # Documents
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    }
    return content_types.get(ext, "application/octet-stream")


async def upload_file(
    file_data: bytes,
    filename: str,
    folder: str = "uploads",
) -> str:
    """
    Upload a file to Supabase Storage.
    
    Returns the public URL of the uploaded file.
    """
    client = get_storage_client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    
    # Generate unique filename to avoid collisions
    ext = get_file_extension(filename)
    unique_name = f"{folder}/{uuid.uuid4()}.{ext}" if ext else f"{folder}/{uuid.uuid4()}"
    
    content_type = get_content_type(filename)
    
    # Upload to Supabase Storage
    client.storage.from_(bucket).upload(
        path=unique_name,
        file=file_data,
        file_options={"content-type": content_type},
    )
    
    # Get public URL
    public_url = client.storage.from_(bucket).get_public_url(unique_name)
    
    return public_url


async def delete_file(file_path: str) -> bool:
    """Delete a file from Supabase Storage."""
    try:
        client = get_storage_client()
        bucket = settings.SUPABASE_STORAGE_BUCKET
        
        # Extract path from full URL if needed
        if file_path.startswith("http"):
            # URL format: https://.../storage/v1/object/public/bucket/path
            parts = file_path.split(f"/storage/v1/object/public/{bucket}/")
            if len(parts) > 1:
                file_path = parts[1]
        
        client.storage.from_(bucket).remove([file_path])
        return True
    except Exception:
        return False
