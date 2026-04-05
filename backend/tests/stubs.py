from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage


def stub_png_upload(name: str = "test.png") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (1, 1), color=(255, 0, 0)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")
