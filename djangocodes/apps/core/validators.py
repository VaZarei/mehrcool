"""Reusable upload validators for images and video.

Each validator raises :class:`django.core.exceptions.ValidationError` with a
plain-English message the admin can act on.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible


def _size_label(num_bytes: int) -> str:
    """Return a human-readable size such as ``'2.5 MB'``.

    Args:
        num_bytes: Size in bytes.

    Returns:
        Formatted size string.
    """
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    return f"{num_bytes / 1024:.0f} KB"


@deconstructible
class MaxFileSizeValidator:
    """Reject files larger than ``max_bytes``.

    Args:
        max_bytes: Maximum allowed size in bytes.
    """

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes

    def __call__(self, value: UploadedFile | FieldFile) -> None:
        """Validate the file size.

        Args:
            value: Uploaded file or stored field file.

        Raises:
            ValidationError: If the file exceeds ``max_bytes``.
        """
        size = getattr(value, "size", None)
        if size is not None and size > self.max_bytes:
            raise ValidationError(
                f"This file is {_size_label(size)}. Please keep it under "
                f"{_size_label(self.max_bytes)} so pages stay fast on mobile."
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MaxFileSizeValidator) and other.max_bytes == self.max_bytes


@deconstructible
class ImageDimensionValidator:
    """Enforce minimum (and optionally exact) raster image dimensions. SVGs are skipped.

    Args:
        min_width: Minimum width in pixels.
        min_height: Minimum height in pixels.
        exact: If ``True`` the image must be exactly ``min_width × min_height``.
    """

    def __init__(self, min_width: int = 0, min_height: int = 0, exact: bool = False) -> None:
        self.min_width = min_width
        self.min_height = min_height
        self.exact = exact

    def __call__(self, value: UploadedFile | FieldFile) -> None:
        """Validate the image dimensions.

        Args:
            value: Uploaded file or stored field file.

        Raises:
            ValidationError: If the image is smaller than required.
        """
        name = (getattr(value, "name", "") or "").lower()
        if name.endswith(".svg"):
            return
        width = getattr(value, "width", None)
        height = getattr(value, "height", None)
        if width is None or height is None:
            try:
                from PIL import Image

                value.open()
                with Image.open(value) as img:
                    width, height = img.size
            except Exception:  # noqa: BLE001 - Pillow errors vary; let ImageField report them
                return
            finally:
                if hasattr(value, "seek"):
                    value.seek(0)
        if self.exact and (width != self.min_width or height != self.min_height):
            raise ValidationError(
                f"This image is {width} × {height} px. It must be exactly "
                f"{self.min_width} × {self.min_height} px."
            )
        if width < self.min_width or height < self.min_height:
            raise ValidationError(
                f"This image is {width} × {height} px. Please upload one at least "
                f"{self.min_width} × {self.min_height} px so it stays sharp on large screens."
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ImageDimensionValidator)
            and other.min_width == self.min_width
            and other.min_height == self.min_height
            and other.exact == self.exact
        )


def validate_image_upload_size(value: UploadedFile | FieldFile) -> None:
    """Validate an image against ``settings.MAX_UPLOAD_IMAGE_BYTES``.

    Args:
        value: The uploaded image.
    """
    MaxFileSizeValidator(settings.MAX_UPLOAD_IMAGE_BYTES)(value)


def validate_video_upload_size(value: UploadedFile | FieldFile) -> None:
    """Validate a video against ``settings.MAX_UPLOAD_VIDEO_BYTES``.

    Args:
        value: The uploaded video.
    """
    MaxFileSizeValidator(settings.MAX_UPLOAD_VIDEO_BYTES)(value)
