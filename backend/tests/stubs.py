from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage

_CONTENT_TYPE_BY_PIL_FORMAT: dict[str, str] = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
}


def stub_image_upload(
    name: str = "test.png", format: str = "PNG"
) -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (1, 1), color=(255, 0, 0)).save(buffer, format)
    content_type = _CONTENT_TYPE_BY_PIL_FORMAT.get(format, "image/png")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)
