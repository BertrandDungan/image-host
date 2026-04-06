from __future__ import annotations

from io import BytesIO
from typing import NamedTuple

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image as PILImage, UnidentifiedImageError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from uuid import uuid4

from backend.models import (
    MAX_STRING_LENGTH,
    AccountTier,
    Image,
    ImageSize,
    User,
)
from backend.serializer import (
    ImageGetUrlsResponseSerializer,
    ImagePutErrorSerializer,
    ImagePutRequestSerializer,
)

_ALLOWED_PIL_FORMATS = frozenset({"PNG", "JPEG"})
_UPLOAD_FIELD = "image"
_USER_ID_FIELD = "user_id"
_FILENAME_FIELD = "filename"
_IMAGE_SIZE_QUERY = "image_size"
_PREMIUM_SIZE_VALUES = frozenset(
    {ImageSize.MEDIUM_THUMBNAIL.value, ImageSize.ORIGINAL.value}
)


class ImageView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary="List image ids and URLs by user and size",
        description=(
            "Returns each image's id and absolute URL for an image owned by the "
            "user at the given size. Medium thumbnails and originals require Premium "
            "or Enterprise."
        ),
        tags=["images"],
        parameters=[
            OpenApiParameter(
                name=_USER_ID_FIELD,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Owner user ID.",
            ),
            OpenApiParameter(
                name=_IMAGE_SIZE_QUERY,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=list(ImageSize.values),
                description="Variant size key (matches `ImageSize`).",
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ImageGetUrlsResponseSerializer,
                description="Matching image ids and URLs (may be empty).",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ImagePutErrorSerializer,
                description="Missing or invalid query parameters, or unknown user.",
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=ImagePutErrorSerializer,
                description="Account tier does not allow this image size.",
            ),
        },
    )
    def get(self, request: Request) -> Response:
        user_id_raw = request.query_params.get(_USER_ID_FIELD)
        if user_id_raw is None or user_id_raw == "":
            return Response(
                {"detail": f"Missing '{_USER_ID_FIELD}' query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_id = int(user_id_raw)
        except (TypeError, ValueError):
            return Response(
                {"detail": f"Invalid '{_USER_ID_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        size = request.query_params.get(_IMAGE_SIZE_QUERY)
        if size is None or size == "":
            return Response(
                {"detail": f"Missing '{_IMAGE_SIZE_QUERY}' query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if size not in ImageSize.values:
            return Response(
                {"detail": f"Invalid '{_IMAGE_SIZE_QUERY}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": f"No user exists with the given id: {user_id}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if size in _PREMIUM_SIZE_VALUES:
            if user.account_tier not in (
                AccountTier.PREMIUM,
                AccountTier.ENTERPRISE,
            ):
                return Response(
                    {
                        "detail": (
                            "Medium thumbnails and original images require a "
                            "Premium or Enterprise account."
                        ),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        items = [
            {
                "id": row.id,
                "url": request.build_absolute_uri(row.image.url),
            }
            for row in Image.objects.filter(owner_id=user_id, size=size).order_by("id")
        ]
        return Response({"items": items})

    @extend_schema(
        summary="Upload image",
        description=(
            "Multipart upload that creates three `Image` objects (small thumbnail, "
            "medium thumbnail, and original)"
        ),
        tags=["images"],
        request=ImagePutRequestSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Three image variants were stored successfully.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ImagePutErrorSerializer,
                description=(
                    "Input validation failure. Failure reason is under `detail` "
                ),
            ),
        },
    )
    def put(self, request: Request) -> Response:
        payload, error = self._validate_put(request)
        if error is not None:
            return error
        assert payload is not None
        return self._save_validated_image(payload)

    class _ValidatedPutPayload(NamedTuple):
        owner: User
        title: str
        raw: bytes
        image_format: str

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

    def _resize_thumbnail(self, raw: bytes, max_dimension: int, format: str) -> bytes:
        """
        Scales image down in place to a thumbnail square of a maximum size
        """
        out = BytesIO()
        with PILImage.open(BytesIO(raw)) as img:
            img.load()
            img.thumbnail((max_dimension, max_dimension))
            img.save(out, format)
        return out.getvalue()

    def _save_validated_image(
        self, payload: ImageView._ValidatedPutPayload
    ) -> Response:
        format = payload.image_format.lower()
        medium_bytes = self._resize_thumbnail(
            payload.raw, int(ImageSize.MEDIUM_THUMBNAIL), format
        )
        small_bytes = self._resize_thumbnail(
            payload.raw, int(ImageSize.SMALL_THUMBNAIL), format
        )

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
                    storage_name = f"{base_id}_{size}.{format}"
                    instance.image.save(storage_name, ContentFile(data), save=False)
                    instance.full_clean()
                    instance.save()
        except ValidationError as exc:
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
