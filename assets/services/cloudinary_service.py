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

class ImaageValidationError(ValueError):
   """The uploaded image is not valid or is in an unsupported format."""

def validate_image(uploaded_file) -> str:
   """ Inspect the file bytes and return the image format if valid, otherwise raise an ImaageValidationError. """

   size = getattr(uploaded_file, "size", None)

   

