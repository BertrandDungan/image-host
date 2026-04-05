from __future__ import annotations

from io import BytesIO
from typing import NamedTuple

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image as PILImage, UnidentifiedImageError
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from uuid import uuid4

from backend.models import MAX_STRING_LENGTH, Image, ImageSize, User

_ALLOWED_PIL_FORMATS = frozenset({"PNG", "JPEG"})
_SMALL_THUMB_MAX_PX = 150
_MEDIUM_THUMB_MAX_PX = 600
_UPLOAD_FIELD = "image"
_USER_ID_FIELD = "user_id"
_FILENAME_FIELD = "filename"


class ImageView(APIView):
    class _ValidatedPutPayload(NamedTuple):
        owner: User
        title: str
        raw: bytes
        image_format: str

    parser_classes = [MultiPartParser]

    def put(self, request: Request) -> Response:
        payload, error = self._validate_put(request)
        if error is not None:
            return error
        assert payload is not None
        return self._save_validated_image(payload)

    def _validate_put(
        self, request: Request
    ) -> tuple[ImageView._ValidatedPutPayload | None, Response | None]:
        """
        Returns a tuple of either the validated payload or
        an error response if it fails validation
        """
        user_id_raw = request.data.get(_USER_ID_FIELD)
        if user_id_raw is None or user_id_raw == "":
            return None, Response(
                {"detail": f"Missing '{_USER_ID_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_id = int(user_id_raw)
        except (TypeError, ValueError):
            return None, Response(
                {"detail": f"Invalid '{_USER_ID_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename_raw = request.data.get(_FILENAME_FIELD)
        if not isinstance(filename_raw, str):
            return None, Response(
                {"detail": f"Invalid '{_FILENAME_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        title = filename_raw.strip()
        if not title:
            return None, Response(
                {"detail": f"'{_FILENAME_FIELD}' must be a non-empty filename."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(title) > MAX_STRING_LENGTH:
            return None, Response(
                {"detail": "Filename exceeds maximum length."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload = request.FILES.get(_UPLOAD_FIELD)
        if upload is None:
            return None, Response(
                {"detail": f"Missing multipart file field '{_UPLOAD_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw = upload.read()
        if not raw:
            return None, Response(
                {"detail": "The uploaded file is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with PILImage.open(BytesIO(raw)) as img:
                image_format = img.format
                img.verify()
        except (UnidentifiedImageError, OSError):
            return None, Response(
                {"detail": "The uploaded file is not a valid image."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if image_format not in _ALLOWED_PIL_FORMATS:
            return None, Response(
                {"detail": "Only PNG and JPEG images are accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None, Response(
                {"detail": f"No user exists with the given id: {user_id}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return (
            self._ValidatedPutPayload(
                owner=owner, title=title, raw=raw, image_format=image_format
            ),
            None,
        )

    def _thumbnail_bytes(self, raw: bytes, max_dimension: int) -> bytes:
        """
        Scales image down in place to a thumbnail square of a maximum size
        """
        out = BytesIO()
        with PILImage.open(BytesIO(raw)) as img:
            img.load()
            img.thumbnail((max_dimension, max_dimension))
            img.save(out)
        return out.getvalue()

    def _save_validated_image(
        self, payload: ImageView._ValidatedPutPayload
    ) -> Response:
        medium_bytes = self._thumbnail_bytes(payload.raw, _MEDIUM_THUMB_MAX_PX)
        small_bytes = self._thumbnail_bytes(payload.raw, _SMALL_THUMB_MAX_PX)

        variants: tuple[tuple[ImageSize, bytes], ...] = (
            (ImageSize.SMALL_THUMBNAIL, small_bytes),
            (ImageSize.MEDIUM_THUMBNAIL, medium_bytes),
            (ImageSize.ORIGINAL, payload.raw),
        )

        base_id = uuid4()
        try:
            with transaction.atomic():
                for size, data in variants:
                    instance = Image(
                        title=payload.title,
                        owner=payload.owner,
                        size=size,
                    )
                    storage_name = f"{base_id}_{size}.{payload.image_format.lower()}"
                    instance.image.save(storage_name, ContentFile(data), save=False)
                    instance.full_clean()
                    instance.save()
        except ValidationError as exc:
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
