from datetime import timedelta
from typing import Any

from django.utils import timezone
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


class ShareLinkCreateSerializer(serializers.Serializer[Any]):
    """JSON body to create a time-limited share link for an image."""

    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(),
        help_text="Primary key of the image to share.",
    )
    expiry_seconds = serializers.IntegerField(
        min_value=300,
        max_value=30000,
        help_text="Seconds until the link expires (inclusive range 300–30000).",
    )

    def create(self, validated_data: dict[str, Any]) -> Share_Link:
        expiry = timezone.now() + timedelta(seconds=validated_data["expiry_seconds"])
        return Share_Link.objects.create(
            image=validated_data["image"],
            expiry=expiry,
        )

    def to_representation(self, instance: Share_Link) -> dict[str, Any]:
        return Share_LinkSerializer(instance).data


class ShareLinkErrorSerializer(serializers.Serializer[Any]):
    """Error body when share link creation validation fails."""

    detail = serializers.CharField(
        required=False,
        help_text="Human-readable error.",
    )


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


class ImageGetUrlsResponseSerializer(serializers.Serializer[Any]):
    """JSON body listing absolute URLs for the requested size."""

    urls = serializers.ListField(
        child=serializers.URLField(),
        help_text="Absolute URLs of stored images for the user and size.",
    )
