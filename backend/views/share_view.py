from typing import Any

from django.http import Http404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from backend.models import Share_Link
from backend.serializer import (
    ImageSerializer,
    ShareLinkCreateSerializer,
    Share_LinkSerializer,
    ShareLinkErrorSerializer,
)


class ShareLinkViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet[Share_Link],
):
    queryset = Share_Link.objects.select_related("image")
    serializer_class = ShareLinkCreateSerializer

    @extend_schema(
        summary="Create share link",
        description=(
            "Creates a `Share_Link` for the given image. Expiry is computed from "
            "now plus `expiry_seconds`."
        ),
        tags=["share-links"],
        request=ShareLinkCreateSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=Share_LinkSerializer,
                description="Share link was created.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ShareLinkErrorSerializer,
                description="Invalid request body or unknown image id.",
            ),
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Get image via share link",
        description=(
            "Returns the `Image` referenced by this share link. The path `id` is "
            "the share link id, not the image id. Responds with 404 if the link "
            "does not exist or `expiry` is in the past."
        ),
        tags=["share-links"],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ImageSerializer,
                description="The shared image.",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Unknown share link, or the link has expired.",
            ),
        },
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        link = self.get_object()
        if timezone.now() > link.expiry:
            raise Http404()
        return Response(ImageSerializer(link.image).data)
