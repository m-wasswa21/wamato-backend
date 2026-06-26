import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from PIL import Image
import io

from app.core.config import settings
from app.core.exceptions import BadRequest


class UploadService:

    @staticmethod
    async def upload_property_image(file: UploadFile, property_id: str) -> Tuple[str, str]:
        await _validate_image(file)
        if settings.use_cloudinary:
            return await _upload_cloudinary(file, f"wamato/properties/{property_id}")
        return await _save_local(file, f"properties/{property_id}")

    @staticmethod
    async def upload_avatar(file: UploadFile, user_id: str) -> str:
        await _validate_image(file)
        if settings.use_cloudinary:
            url, _ = await _upload_cloudinary(file, f"wamato/avatars/{user_id}")
            return url
        url, _ = await _save_local(file, f"avatars/{user_id}")
        return url


async def _validate_image(file: UploadFile) -> None:
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise BadRequest(f"Unsupported file type: {file.content_type}")
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise BadRequest(f"File too large. Max {settings.MAX_FILE_SIZE_MB} MB")
    await file.seek(0)


async def _save_local(file: UploadFile, sub_path: str) -> Tuple[str, str]:
    dest_dir = Path(settings.UPLOAD_DIR) / sub_path
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "img.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = dest_dir / filename
    content = await file.read()
    filepath.write_bytes(content)

    # Generate thumbnail
    thumb_filename = f"thumb_{filename}"
    thumb_path = dest_dir / thumb_filename
    img = Image.open(io.BytesIO(content))
    img.thumbnail((400, 300))
    img.save(str(thumb_path))

    base_url = f"/{settings.UPLOAD_DIR}/{sub_path}"
    return f"{base_url}/{filename}", f"{base_url}/{thumb_filename}"


async def _upload_cloudinary(file: UploadFile, folder: str) -> Tuple[str, str]:
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )
    content = await file.read()
    result = cloudinary.uploader.upload(
        content,
        folder=folder,
        transformation=[{"width": 1200, "height": 900, "crop": "limit", "quality": "auto"}],
    )
    thumb = cloudinary.uploader.upload(
        content,
        folder=folder,
        transformation=[{"width": 400, "height": 300, "crop": "fill", "quality": "auto"}],
    )
    return result["secure_url"], thumb["secure_url"]
