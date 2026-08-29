"""Cloudinary service module for handling image uploads and transformations."""
from __future__ import annotations

from PIL import Image, UnidentifiedImageError


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