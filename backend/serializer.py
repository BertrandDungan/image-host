from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from backend.models import MAX_STRING_LENGTH, User, Image, Share_Link


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "name", "account_tier"]


class ImageSerializer(serializers.ModelSerializer[Image]):
    class Meta:
        model = Image
        fields = ["id", "title", "owner", "image", "size"]


class Share_LinkSerializer(serializers.ModelSerializer[Share_Link]):
    class Meta:
        model = Share_Link
        fields = ["id", "image", "expiry"]


@extend_schema_field(OpenApiTypes.BINARY)
class _MultipartBinaryFileField(serializers.FileField):
    """FileField documented as binary for multipart OpenAPI request bodies."""


class ImagePutRequestSerializer(serializers.Serializer[Any]):
    """Multipart body for uploading an image."""

    user_id = serializers.IntegerField(
        help_text="ID of the user who will own the uploaded image.",
    )
    filename = serializers.CharField(max_length=MAX_STRING_LENGTH)
    image = _MultipartBinaryFileField(
        help_text="Image file. Only PNG and JPEG are accepted.",
    )


class ImagePutErrorSerializer(serializers.Serializer[Any]):
    """Error body when validation fails before persistence."""

    detail = serializers.CharField(
        required=False,
        help_text="Human-readable error.",
    )
