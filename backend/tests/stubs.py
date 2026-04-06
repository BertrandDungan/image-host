import shutil
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage

# Subdirectory under the project's MEDIA_ROOT where test runs store uploaded files.
STUB_MEDIA_TESTS_SUBDIR = "tests"

_CONTENT_TYPE_BY_PIL_FORMAT: dict[str, str] = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
}


def stub_media_tests_path() -> Path:
    """Filesystem directory used as MEDIA_ROOT for tests (…/MEDIA_ROOT/tests/)."""
    return Path(settings.MEDIA_ROOT).resolve() / STUB_MEDIA_TESTS_SUBDIR


def stub_image_upload(
    name: str = "test.png", format: str = "PNG"
) -> SimpleUploadedFile:
    """Build a small in-memory upload. On save, Django writes under the active MEDIA_ROOT."""
    buffer = BytesIO()
    PILImage.new("RGB", (1, 1), color=(255, 0, 0)).save(buffer, format)
    content_type = _CONTENT_TYPE_BY_PIL_FORMAT.get(format, "image/png")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


class StubMediaTestCase(TestCase):
    """Use MEDIA_ROOT/<tests>/ for file fields and remove that directory after the class."""

    _stub_media_root: Path
    _media_settings: override_settings

    @classmethod
    def setUpClass(cls) -> None:
        cls._stub_media_root = stub_media_tests_path()
        cls._stub_media_root.mkdir(parents=True, exist_ok=True)
        cls._media_settings = override_settings(MEDIA_ROOT=cls._stub_media_root)
        cls._media_settings.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls._media_settings.disable()
        shutil.rmtree(cls._stub_media_root, ignore_errors=True)
