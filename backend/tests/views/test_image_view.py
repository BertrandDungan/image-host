from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from backend.models import MAX_STRING_LENGTH, AccountTier, Image, User
from backend.views.image_view import ImageView

from ..stubs import stub_image_upload


class ImageViewTests(TestCase):
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
    ):
        data: dict = {}
        if user_id is not None:
            data["user_id"] = user_id
        if filename is not None:
            data["filename"] = filename
        if image is not None:
            data["image"] = image
        request = self.factory.put("/", data, format="multipart")
        return self.view(request)

    def test_put_saves_png_and_returns_204(self) -> None:
        upload = stub_image_upload("my_photo.png")
        response = self._put(
            user_id=self.user.pk,
            filename="my_photo.png",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 1)
        row = Image.objects.get()
        self.assertEqual(row.title, "my_photo.png")
        self.assertEqual(row.owner_id, self.user.pk)
        self.assertTrue(row.image.name)
        self.assertTrue(row.image.storage.exists(row.image.name))

    def test_put_accepts_jpeg(self) -> None:
        upload = stub_image_upload("test.jpg", format="JPEG")
        response = self._put(
            user_id=self.user.pk,
            filename="shot.jpg",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 1)

    def test_put_strips_path_from_filename_for_title(self) -> None:
        upload = stub_image_upload()
        response = self._put(
            user_id=self.user.pk,
            filename="  folder/nested/name.png  ",
            image=upload,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.get().title, "name.png")

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

    def test_put_rejects_non_string_filename(self) -> None:
        # Multipart encoding stringifies field values; call put() with a duck-typed request.
        upload = stub_image_upload()
        uid = str(self.user.pk)

        class _Data:
            @staticmethod
            def get(key: str, default=None):
                return {"user_id": uid, "filename": 123}.get(key, default)

        class _Files:
            @staticmethod
            def get(key: str, default=None):
                return upload if key == "image" else default

        class _Req:
            data = _Data()
            FILES = _Files()

        response = ImageView().put(_Req())
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
