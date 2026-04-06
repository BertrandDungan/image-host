from io import BytesIO
from unittest.mock import patch
from typing import Any

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APIRequestFactory

from backend.models import MAX_STRING_LENGTH, AccountTier, Image, ImageSize, User
from backend.views.image_view import ImageView


from ..stubs import StubMediaTestCase, stub_image_upload


MEDIUM_PX = int(ImageSize.MEDIUM_THUMBNAIL)
SMALL_PX = int(ImageSize.SMALL_THUMBNAIL)


class ImageViewTests(StubMediaTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.view = ImageView.as_view()
        self.user = User.objects.create(name="uploader", account_tier=AccountTier.BASIC)

    def _put(
        self,
        *,
        user_id: str | int | None = None,
        filename: str | None = "photo.png",
        image: SimpleUploadedFile | None = None,
    ) -> Any:
        data: dict[str, str | int | SimpleUploadedFile | None] = {}
        if user_id is not None:
            data["user_id"] = user_id
        if filename is not None:
            data["filename"] = filename
        if image is not None:
            data["image"] = image
        request = self.factory.put("/", data, format="multipart")
        return self.view(request)

    def _get(
        self,
        *,
        user_id: str | int | None = None,
        image_size: str | None = None,
    ) -> Any:
        q: list[tuple[str, str]] = []
        if user_id is not None:
            q.append(("user_id", str(user_id)))
        if image_size is not None:
            q.append(("image_size", image_size))
        request = self.factory.get("/", q)
        return self.view(request)

    def test_put_saves_png_and_returns_204(self) -> None:
        upload = stub_image_upload("my_photo.png")
        response = self._put(
            user_id=self.user.pk,
            filename="my_photo.png",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 3)
        by_size = {row.size: row for row in Image.objects.all()}
        self.assertEqual(set(by_size), set(ImageSize.values))
        for row in by_size.values():
            self.assertEqual(row.title, "my_photo.png")
            self.assertEqual(row.owner_id, self.user.pk)
            self.assertTrue(row.image.name and row.image.storage.exists(row.image.name))

    def test_put_saves_three_sizes_with_expected_dimensions(self) -> None:
        orig_w, orig_h = 1200, 800
        buffer = BytesIO()
        PILImage.new("RGB", (orig_w, orig_h), color=(10, 20, 30)).save(
            buffer, format="PNG"
        )
        upload = SimpleUploadedFile(
            "large.png", buffer.getvalue(), content_type="image/png"
        )
        response = self._put(
            user_id=self.user.pk,
            filename="large.png",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 3)
        by_size = {row.size: row for row in Image.objects.all()}

        small = by_size[ImageSize.SMALL_THUMBNAIL]
        self.assertLessEqual(small.image.width, SMALL_PX)
        self.assertLessEqual(small.image.height, SMALL_PX)
        self.assertEqual(max(small.image.width, small.image.height), SMALL_PX)

        medium = by_size[ImageSize.MEDIUM_THUMBNAIL]
        self.assertLessEqual(medium.image.width, MEDIUM_PX)
        self.assertLessEqual(medium.image.height, MEDIUM_PX)
        self.assertEqual(max(medium.image.width, medium.image.height), MEDIUM_PX)

        original = by_size[ImageSize.ORIGINAL]
        self.assertEqual(original.image.width, orig_w)
        self.assertEqual(original.image.height, orig_h)

    def test_put_accepts_jpeg(self) -> None:
        upload = stub_image_upload("test.jpg", format="JPEG")
        response = self._put(
            user_id=self.user.pk,
            filename="shot.jpg",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 3)

    def test_put_uses_trimmed_filename_for_title(self) -> None:
        upload = stub_image_upload()
        filename = "  folder/nested/name.png  "
        response = self._put(
            user_id=self.user.pk,
            filename=filename,
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 3)
        expected_title = filename.strip()
        self.assertTrue(all(row.title == expected_title for row in Image.objects.all()))

    def test_put_rejects_missing_user_id(self) -> None:
        response = self._put(user_id=None, filename="a.png", image=stub_image_upload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Missing 'user_id'.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_empty_user_id(self) -> None:
        response = self._put(user_id="", filename="a.png", image=stub_image_upload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Missing 'user_id'.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_invalid_user_id(self) -> None:
        response = self._put(
            user_id="not-an-int",
            filename="a.png",
            image=stub_image_upload(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid 'user_id'.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_missing_filename(self) -> None:
        response = self._put(
            user_id=self.user.pk,
            filename=None,
            image=stub_image_upload(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid 'filename'.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_blank_filename(self) -> None:
        response = self._put(
            user_id=self.user.pk,
            filename="   ",
            image=stub_image_upload(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "'filename' must be a non-empty filename.",
        )
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_filename_exceeding_max_length(self) -> None:
        long_name = "x" * (MAX_STRING_LENGTH + 1)
        response = self._put(
            user_id=self.user.pk,
            filename=long_name,
            image=stub_image_upload(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Filename exceeds maximum length.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_missing_image_field(self) -> None:
        response = self._put(user_id=self.user.pk, filename="a.png", image=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Missing multipart file field 'image'.",
        )
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_empty_upload(self) -> None:
        empty = SimpleUploadedFile("empty.png", b"", content_type="image/png")
        response = self._put(
            user_id=self.user.pk,
            filename="empty.png",
            image=empty,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "The uploaded file is empty.")
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_non_image_bytes(self) -> None:
        bad = SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")
        response = self._put(
            user_id=self.user.pk,
            filename="fake.png",
            image=bad,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "The uploaded file is not a valid image.",
        )
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_unsupported_image_format(self) -> None:
        upload = stub_image_upload("test.gif", format="GIF")
        response = self._put(
            user_id=self.user.pk,
            filename="anim.gif",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Only PNG and JPEG images are accepted.",
        )
        self.assertEqual(Image.objects.count(), 0)

    def test_put_rejects_unknown_user(self) -> None:
        response = self._put(
            user_id=9_999_999,
            filename="a.png",
            image=stub_image_upload(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "No user exists with the given id: 9999999.",
        )
        self.assertEqual(Image.objects.count(), 0)

    def test_put_returns_model_validation_errors_from_full_clean(self) -> None:
        upload = stub_image_upload()

        def boom(_self: Image) -> None:
            raise ValidationError({"title": ["Invalid title."]})

        with patch.object(Image, "full_clean", boom):
            response = self._put(
                user_id=self.user.pk,
                filename="ok.png",
                image=upload,
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"title": ["Invalid title."]})
        self.assertEqual(Image.objects.count(), 0)

    def test_get_returns_small_thumbnail_urls_for_basic_tier(self) -> None:
        upload = stub_image_upload("a.png")
        self._put(user_id=self.user.pk, filename="a.png", image=upload)
        small = Image.objects.get(size=ImageSize.SMALL_THUMBNAIL)
        response = self._get(
            user_id=self.user.pk,
            image_size=ImageSize.SMALL_THUMBNAIL.value,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["id"], small.id)
        self.assertTrue(
            response.data["items"][0]["url"].endswith(small.image.name)
        )

    def test_get_forbids_medium_thumbnail_for_basic_tier(self) -> None:
        upload = stub_image_upload("a.png")
        self._put(user_id=self.user.pk, filename="a.png", image=upload)
        response = self._get(
            user_id=self.user.pk,
            image_size=ImageSize.MEDIUM_THUMBNAIL.value,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_get_forbids_original_for_basic_tier(self) -> None:
        upload = stub_image_upload("a.png")
        self._put(user_id=self.user.pk, filename="a.png", image=upload)
        response = self._get(
            user_id=self.user.pk,
            image_size=ImageSize.ORIGINAL.value,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_returns_medium_and_original_urls_for_premium_tier(self) -> None:
        premium = User.objects.create(
            name="vip",
            account_tier=AccountTier.PREMIUM,
        )
        upload = stub_image_upload("b.png")
        self._put(user_id=premium.pk, filename="b.png", image=upload)
        for size in (ImageSize.MEDIUM_THUMBNAIL, ImageSize.ORIGINAL):
            row = Image.objects.get(owner_id=premium.pk, size=size)
            response = self._get(user_id=premium.pk, image_size=size.value)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["items"]), 1)
            self.assertEqual(response.data["items"][0]["id"], row.id)
            self.assertTrue(
                response.data["items"][0]["url"].endswith(row.image.name)
            )

    def test_get_rejects_missing_user_id(self) -> None:
        response = self._get(user_id=None, image_size=ImageSize.SMALL_THUMBNAIL.value)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rejects_missing_image_size(self) -> None:
        response = self._get(user_id=self.user.pk, image_size=None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rejects_invalid_image_size(self) -> None:
        response = self._get(user_id=self.user.pk, image_size="huge")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rejects_unknown_user(self) -> None:
        response = self._get(
            user_id=9_999_999,
            image_size=ImageSize.SMALL_THUMBNAIL.value,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
