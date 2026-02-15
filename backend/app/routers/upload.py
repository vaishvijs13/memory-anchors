from __future__ import annotations

"""Upload router for file-based memory creation with LLM generation."""

import base64
import io
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import get_llm_provider, get_vision_provider
from ..ai.prompts import (
    AUDIO_MEMORY_PROMPT,
    DOCUMENT_MEMORY_PROMPT,
    FILE_MEMORY_SYSTEM,
    IMAGE_MEMORY_PROMPT,
    MULTI_FILE_MEMORY_PROMPT,
)
from ..dependencies import get_db
from ..models.memory import Memory, MemoryEmotion, MemoryObject, MemoryPerson
from ..models.object import RegisteredObject
from ..models.user import User
from ..services.storage_service import upload_file, get_file_extension

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadMemoryResponse(BaseModel):
    object_label: str
    title: str
    memory_text: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    file_urls: List[str] = []


def _get_file_type(filename: str) -> str:
    """Determine file type category from filename."""
    ext = get_file_extension(filename)
    image_exts = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}
    video_exts = {"mp4", "webm", "mov", "avi"}
    audio_exts = {"mp3", "wav", "m4a", "ogg", "flac"}
    doc_exts = {"pdf", "doc", "docx", "txt", "rtf"}
    
    if ext in image_exts:
        return "image"
    elif ext in video_exts:
        return "video"
    elif ext in audio_exts:
        return "audio"
    elif ext in doc_exts:
        return "document"
    return "unknown"


async def _extract_text_from_pdf(file_data: bytes) -> str:
    """Extract text from PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_data))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Could not extract PDF text: {e}]"


async def _extract_text_from_docx(file_data: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"[Could not extract DOCX text: {e}]"


async def _extract_text_from_txt(file_data: bytes) -> str:
    """Extract text from plain text file."""
    try:
        return file_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return file_data.decode("latin-1")
        except Exception:
            return "[Could not decode text file]"


async def _process_document(file_data: bytes, filename: str) -> str:
    """Extract text from document based on file type."""
    ext = get_file_extension(filename)
    if ext == "pdf":
        return await _extract_text_from_pdf(file_data)
    elif ext == "docx":
        return await _extract_text_from_docx(file_data)
    elif ext in ("txt", "rtf"):
        return await _extract_text_from_txt(file_data)
    elif ext == "doc":
        return "[.doc format not supported - please convert to .docx]"
    return "[Unknown document format]"


async def _generate_memory_from_image(
    image_data: bytes, object_label: str
) -> dict:
    """Use GPT-4o vision to analyze image and generate memory."""
    vision = get_vision_provider()
    
    # Convert to base64
    b64_image = base64.b64encode(image_data).decode("utf-8")
    
    prompt = IMAGE_MEMORY_PROMPT.format(object_label=object_label)
    
    # Use vision to analyze and generate memory in one call
    full_prompt = f"""{prompt}

{FILE_MEMORY_SYSTEM}"""
    
    raw_response = await vision.analyze_image(b64_image, full_prompt)
    
    return _parse_memory_json(raw_response, object_label)


async def _generate_memory_from_document(
    document_text: str, object_label: str
) -> dict:
    """Use GPT-4 to generate memory from document text."""
    llm = get_llm_provider()
    
    # Truncate if too long
    max_chars = 4000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[... document truncated ...]"
    
    prompt = DOCUMENT_MEMORY_PROMPT.format(
        object_label=object_label,
        document_text=document_text,
    )
    
    raw_response = await llm.generate_text(prompt, system=FILE_MEMORY_SYSTEM)
    
    return _parse_memory_json(raw_response, object_label)


async def _generate_memory_from_audio(
    transcription: str, object_label: str
) -> dict:
    """Use GPT-4 to generate memory from audio transcription."""
    llm = get_llm_provider()
    
    prompt = AUDIO_MEMORY_PROMPT.format(
        object_label=object_label,
        transcription=transcription,
    )
    
    raw_response = await llm.generate_text(prompt, system=FILE_MEMORY_SYSTEM)
    
    return _parse_memory_json(raw_response, object_label)


async def _transcribe_audio(audio_data: bytes, filename: str) -> str:
    """Transcribe audio using OpenAI Whisper."""
    try:
        from openai import AsyncOpenAI
        from ..config import settings
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Create a file-like object
        ext = get_file_extension(filename)
        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"audio.{ext}"
        
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        
        return transcription.text
    except Exception as e:
        return f"[Could not transcribe audio: {e}]"


def _parse_memory_json(raw_response: str, object_label: str) -> dict:
    """Parse LLM response into memory data dict."""
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block
        if "```" in raw_response:
            json_str = raw_response.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            try:
                data = json.loads(json_str.strip())
            except json.JSONDecodeError:
                data = {
                    "title": f"Memory of {object_label}",
                    "narrative": raw_response,
                }
        else:
            data = {
                "title": f"Memory of {object_label}",
                "narrative": raw_response,
            }
    
    return {
        "title": data.get("title", f"Memory of {object_label}"),
        "narrative": data.get("narrative", raw_response),
        "emotions": data.get("emotions", []),
        "people": data.get("people", []),
        "sensory_details": data.get("sensory_details"),
    }


@router.post("/memory", response_model=UploadMemoryResponse)
async def upload_memory(
    files: List[UploadFile] = File(...),
    object_label: str = Form(...),
    title: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload files and generate a memory using AI.
    
    Accepts images, documents (PDF, DOCX, TXT), and audio files.
    Uses GPT-4o for image analysis and GPT-4 for text/audio processing.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    label = object_label.lower().strip()
    
    # Get default user (for legacy compatibility)
    default_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
    if default_user is None:
        raise HTTPException(status_code=500, detail="No user exists. Run seed.py first.")
    user_id = default_user.id
    
    # Process each file
    file_urls: List[str] = []
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    
    # Categorize files
    images = []
    documents = []
    audios = []
    
    for f in files:
        file_data = await f.read()
        file_type = _get_file_type(f.filename or "unknown")
        
        # Upload to storage
        url = await upload_file(file_data, f.filename or "file", folder=f"memories/{label}")
        file_urls.append(url)
        
        if file_type == "image":
            images.append((file_data, f.filename, url))
            if not image_url:
                image_url = url
        elif file_type == "document":
            documents.append((file_data, f.filename, url))
        elif file_type == "audio":
            audios.append((file_data, f.filename, url))
            if not audio_url:
                audio_url = url
    
    # Generate memory based on files
    memory_data: Optional[dict] = None
    
    if images:
        # Use first image for vision-based generation
        img_data, img_name, _ = images[0]
        memory_data = await _generate_memory_from_image(img_data, label)
    elif documents:
        # Extract and combine document text
        all_text = []
        for doc_data, doc_name, _ in documents:
            text = await _process_document(doc_data, doc_name or "doc")
            all_text.append(text)
        combined_text = "\n\n---\n\n".join(all_text)
        memory_data = await _generate_memory_from_document(combined_text, label)
    elif audios:
        # Transcribe first audio and generate
        aud_data, aud_name, _ = audios[0]
        transcription = await _transcribe_audio(aud_data, aud_name or "audio.mp3")
        memory_data = await _generate_memory_from_audio(transcription, label)
    else:
        raise HTTPException(
            status_code=400,
            detail="No supported file types found. Please upload images, documents, or audio."
        )
    
    # Use provided title or generated one
    final_title = title.strip() if title and title.strip() else memory_data["title"]
    
    # Find or create registered object
    obj_result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.label == label, RegisteredObject.user_id == user_id
        )
    )
    obj = obj_result.scalar_one_or_none()
    if obj is None:
        obj = RegisteredObject(user_id=user_id, label=label, coco_label=label)
        db.add(obj)
        await db.flush()
    
    # Create memory record
    memory = Memory(
        user_id=user_id,
        title=final_title,
        narrative_text=memory_data["narrative"],
        sensory_details=memory_data.get("sensory_details"),
        image_url=image_url,
        audio_url=audio_url,
        is_ai_generated=True,
        ai_model_used="gpt-4o",
    )
    db.add(memory)
    await db.flush()
    
    # Link to object
    link = MemoryObject(memory_id=memory.id, object_id=obj.id, is_primary=True)
    db.add(link)
    
    # Add emotions
    for em in memory_data.get("emotions", []):
        if isinstance(em, dict) and em.get("emotion"):
            db.add(MemoryEmotion(
                memory_id=memory.id,
                emotion=em.get("emotion", ""),
                intensity=em.get("intensity", 0.5),
            ))
    
    # Add people
    for p in memory_data.get("people", []):
        if isinstance(p, dict) and p.get("name"):
            db.add(MemoryPerson(
                memory_id=memory.id,
                person_name=p.get("name", ""),
                relationship_type=p.get("relationship"),
            ))
    
    await db.commit()
    
    return UploadMemoryResponse(
        object_label=label,
        title=final_title,
        memory_text=memory_data["narrative"],
        audio_url=audio_url,
        image_url=image_url,
        file_urls=file_urls,
    )
