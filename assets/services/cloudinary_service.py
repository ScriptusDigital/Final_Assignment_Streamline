"""Cloudinary service module for handling image uploads and transformations."""
from __future__ import annotations

from PIL import Image, UnidentifiedImageError
from urllib.parse import urlparse, unquote

import cloudinary
from django.conf import settings
import cloudinary.uploader


MAX_UPLOAD_BYTES = 10 * 1024 * 1024

ALLOWED_PIL_FORMATS = {
    "JPEG": "JPEG",
    "PNG": "PNG",
    "GIF": "GIF",
    "BMP": "BMP",
    "TIFF": "TIFF",
    "WEBP": "WEBP",
}

class ImageValidationError(ValueError):
    """The uploaded image is not valid or is in an unsupported format."""


class CloudinaryUploadError(RuntimeError):
    """An error occurred while uploading the image to Cloudinary."""

def validate_image(uploaded_file) -> str:
    """Inspect the actual file bytes and return its image format."""

    size = getattr(uploaded_file, "size", None)

    if size is None:
        position = uploaded_file.tell()
        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(position)

    if size <= 0:
        raise ImageValidationError(
            "The uploaded file is empty."
        )

    if size > MAX_UPLOAD_BYTES:
        raise ImageValidationError(
            "Images must be no larger than 10 MB."
        )

    try:
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as image:
            image_format = (
                image.format or ""
            ).upper()

            if image_format not in ALLOWED_PIL_FORMATS:
                raise ImageValidationError(
                    "Only JPEG, PNG and WebP images are supported."
                )

            image.verify()

    except ImageValidationError:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
    ) as exc:
        raise ImageValidationError(
            "The uploaded file is not a valid image."
        ) from exc

    finally:
        uploaded_file.seek(0)

    return image_format.lower()

def upload_image(uploaded_file) -> dict:
    """Upload an image to Cloudinary and return the upload result."""

    validated_format = validate_image(
        uploaded_file
    )

    _configure_cloudinary()

    folder = getattr(settings, "CLOUDINARY_UPLOAD_FOLDER", "streamline/assets")

    try:
        response = cloudinary.uploader.upload(
            uploaded_file,
            folder=folder,
            resource_type="image",
            type="authenticated",
            use_filename=False,
            unique_filename=True,
            overwrite=False,
        )

    except Exception as exc:
        raise CloudinaryUploadError(
            "The image could not be uploaded. "
            "Please try again."
        ) from exc

    required_fields = (
        "asset_id",
        "public_id",
        "secure_url",
        "width",
        "height",
        "bytes",
    )

    incomplete = any(
        response.get(field) in (None, "") for field in required_fields)
    


    if incomplete:
        public_id = response.get("public_id")

        if public_id:
            destroy_image(
                public_id,
                delivery_type=response.get(
                    "type",
                    "authenticated",
                ),
            )

        raise CloudinaryUploadError(
            "Cloudinary returned an incomplete "
            "upload response."
        )

    return {
        "cloudinary_asset_id": response["asset_id"],
        "public_id": response["public_id"],
        "delivery_type": response.get("type", "authenticated"),
        "secure_url": response["secure_url"],
        "original_filename": str(response.get("original_filename") or getattr(uploaded_file, "name", "") or "")
        ["255"],
        "image_format": (
            response.get("format")
            or validated_format
        ),
        "width": response["width"],
        "height": response["height"],
        "bytes": response["bytes"],
        "version": response.get("version"),
    }

def destroy_image(public_id: str, *, delivery_type: str = "authenticated") -> None:
    """Delete an image from Cloudinary using its public ID."""

    try:
        _configure_cloudinary()

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            type=delivery_type,
            invalidate=True,
        )

    except Exception:
        return


def _configure_cloudinary() -> None:
    """ Load server-side Cloudinary configuration from Django settings. """

    storage = (getattr(settings, "CLOUDINARY_STORAGE", {}) or {})

    cloud_name = storage.get("CLOUD_NAME", "")
    api_key = storage.get("API_KEY", "")
    api_secret = storage.get("API_SECRET", "")

    if not all((cloud_name, api_key, api_secret)):
        cloudinary_url = getattr(settings, "CLOUDINARY_URL", "",)

        if cloudinary_url:
            parsed = urlparse(cloudinary_url)

            if parsed.scheme != "cloudinary":
                cloud_name = parsed.hostname
                api_key = unquote(parsed.username or "")
                api_secret = unquote(parsed.password or "")

    if all((cloud_name, api_key, api_secret)):
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )