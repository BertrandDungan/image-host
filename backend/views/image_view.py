from io import BytesIO
from os import path
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image as PILImage, UnidentifiedImageError
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from uuid import uuid4

from backend.models import MAX_STRING_LENGTH, Image, User

_ALLOWED_PIL_FORMATS = frozenset({"PNG", "JPEG"})
_UPLOAD_FIELD = "image"
_USER_ID_FIELD = "user_id"
_FILENAME_FIELD = "filename"


class ImageView(APIView):
    parser_classes = [MultiPartParser]

    def put(self, request: Request) -> Response:
        user_id_raw = request.data.get(_USER_ID_FIELD)
        if user_id_raw is None or user_id_raw == "":
            return Response(
                {"detail": f"Missing '{_USER_ID_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_id = int(user_id_raw)
        except (TypeError, ValueError):
            return Response(
                {"detail": f"Invalid '{_USER_ID_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename_raw = request.data.get(_FILENAME_FIELD)
        if not isinstance(filename_raw, str):
            return Response(
                {"detail": f"Invalid '{_FILENAME_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        title = path.basename(filename_raw.strip())
        if not title:
            return Response(
                {"detail": f"'{_FILENAME_FIELD}' must be a non-empty filename."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(title) > MAX_STRING_LENGTH:
            return Response(
                {"detail": "Filename exceeds maximum length."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload = request.FILES.get(_UPLOAD_FIELD)
        if upload is None:
            return Response(
                {"detail": f"Missing multipart file field '{_UPLOAD_FIELD}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw = upload.read()
        if not raw:
            return Response(
                {"detail": "The uploaded file is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with PILImage.open(BytesIO(raw)) as img:
                image_format = img.format
                img.verify()
        except (UnidentifiedImageError, OSError):
            return Response(
                {"detail": "The uploaded file is not a valid image."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if image_format not in _ALLOWED_PIL_FORMATS:
            return Response(
                {"detail": "Only PNG and JPEG images are accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": f"No user exists with the given id: {user_id}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = Image(title=title, owner=owner)
        # UUID so that that no saved files collide
        storage_name = f"{uuid4()}.{image_format.lower()}"
        instance.image.save(storage_name, ContentFile(raw), save=False)
        try:
            instance.full_clean()
        except ValidationError as exc:
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
