"""Cloudinary service module for handling image uploads and transformations."""
from __future__ import annotations
from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

ALLOWED_PILLOW_FORMATS = {
    "JPEG": "JPEG",
    "PNG": "PNG",
    "GIF": "GIF",
    "BMP": "BMP",
    "TIFF": "TIFF",
    "WEBP": "WEBP",
}