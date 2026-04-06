from datetime import timedelta
from typing import Any

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory

from backend.models import AccountTier, Image, ImageSize, Share_Link, User
from backend.views.share_view import ShareLinkViewSet

from ..stubs import StubMediaTestCase, stub_image_upload


class ShareLinkViewSetTests(StubMediaTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.create_view = ShareLinkViewSet.as_view({"post": "create"})
        self.retrieve_view = ShareLinkViewSet.as_view({"get": "retrieve"})
        self.user = User.objects.create(name="owner", account_tier=AccountTier.BASIC)

    def _create_image(self) -> Image:
        upload = stub_image_upload("shared.png")
        return Image.objects.create(
            title="shared.png",
            owner=self.user,
            size=ImageSize.SMALL_THUMBNAIL,
            image=upload,
        )

    def _post_create(self, data: dict[str, Any] | None) -> Any:
        request = self.factory.post("/", data or {}, format="json")
        return self.create_view(request)

    def _get_retrieve(self, pk: int | str) -> Any:
        request = self.factory.get("/")
        return self.retrieve_view(request, pk=str(pk))

    def test_create_returns_201_and_share_link_payload(self) -> None:
        image = self._create_image()
        before = timezone.now()
        response = self._post_create({"image": image.pk, "expiry_seconds": 600})
        after = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Share_Link.objects.count(), 1)
        link = Share_Link.objects.get()
        self.assertEqual(link.image_id, image.pk)
        self.assertGreaterEqual(link.expiry, before + timedelta(seconds=600))
        self.assertLessEqual(link.expiry, after + timedelta(seconds=600))
        self.assertEqual(response.data["id"], link.pk)
        self.assertEqual(response.data["image"], image.pk)
        self.assertEqual(
            response.data["expiry"], link.expiry.isoformat().replace("+00:00", "Z")
        )
        expected_url = reverse("share_link-detail", kwargs={"pk": link.pk})
        self.assertEqual(response.data["url"], f"http://testserver{expected_url}")

    def test_create_accepts_minimum_expiry_seconds(self) -> None:
        image = self._create_image()
        response = self._post_create({"image": image.pk, "expiry_seconds": 300})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_accepts_maximum_expiry_seconds(self) -> None:
        image = self._create_image()
        response = self._post_create({"image": image.pk, "expiry_seconds": 30000})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_unknown_image_id(self) -> None:
        response = self._post_create({"image": 9_999_999, "expiry_seconds": 600})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data)
        self.assertEqual(Share_Link.objects.count(), 0)

    def test_create_rejects_expiry_below_minimum(self) -> None:
        image = self._create_image()
        response = self._post_create({"image": image.pk, "expiry_seconds": 299})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expiry_seconds", response.data)
        self.assertEqual(Share_Link.objects.count(), 0)

    def test_create_rejects_expiry_above_maximum(self) -> None:
        image = self._create_image()
        response = self._post_create({"image": image.pk, "expiry_seconds": 30001})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expiry_seconds", response.data)
        self.assertEqual(Share_Link.objects.count(), 0)

    def test_create_rejects_missing_image(self) -> None:
        response = self._post_create({"expiry_seconds": 600})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data)
        self.assertEqual(Share_Link.objects.count(), 0)

    def test_create_rejects_missing_expiry_seconds(self) -> None:
        image = self._create_image()
        response = self._post_create({"image": image.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expiry_seconds", response.data)
        self.assertEqual(Share_Link.objects.count(), 0)

    def test_retrieve_redirects_to_image_url(self) -> None:
        image = self._create_image()
        link = Share_Link.objects.create(
            image=image,
            expiry=timezone.now() + timedelta(hours=1),
        )
        response = self._get_retrieve(link.pk)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], image.image.url)

    def test_retrieve_returns_404_for_unknown_share_link(self) -> None:
        response = self._get_retrieve(9_999_999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_returns_404_when_link_expired(self) -> None:
        image = self._create_image()
        link = Share_Link.objects.create(
            image=image,
            expiry=timezone.now() - timedelta(seconds=1),
        )
        response = self._get_retrieve(link.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
