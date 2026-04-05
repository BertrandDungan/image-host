from django.test import TestCase
from django.utils import timezone
from rest_framework.fields import DateTimeField as DRFSerializerDateTimeField

from backend.models import AccountTier, Image, Share_Link, User
from backend.serializer import ImageSerializer, Share_LinkSerializer, UserSerializer
from .stubs import stub_image_upload


class UserSerializerTests(TestCase):
    def test_serialize_outputs_expected_format(self) -> None:
        user = User.objects.create(name="Alice", account_tier=AccountTier.PREMIUM)
        data = UserSerializer(user).data
        self.assertEqual(
            data,
            {"id": user.pk, "name": "Alice", "account_tier": AccountTier.PREMIUM},
        )

    def test_create_rejects_missing_name(self) -> None:
        serializer = UserSerializer(data={"account_tier": AccountTier.BASIC})
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_create_rejects_missing_account_tier(self) -> None:
        serializer = UserSerializer(data={"name": "Bob"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("account_tier", serializer.errors)

    def test_create_rejects_invalid_account_tier(self) -> None:
        serializer = UserSerializer(data={"name": "Bob", "account_tier": "Pro"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("account_tier", serializer.errors)


class ImageSerializerTests(TestCase):
    def test_serialize_outputs_expected_format(self) -> None:
        owner = User.objects.create(name="owner", account_tier=AccountTier.BASIC)
        image = Image.objects.create(
            title="Photo", owner=owner, image=stub_image_upload("photo.png")
        )
        data = ImageSerializer(image).data
        self.assertEqual(
            data,
            {
                "id": image.pk,
                "title": "Photo",
                "owner": owner.pk,
                "image": image.image.url,
            },
        )

    def test_create_rejects_missing_title(self) -> None:
        owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        serializer = ImageSerializer(
            data={"owner": owner.pk, "image": stub_image_upload()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_create_rejects_missing_owner(self) -> None:
        serializer = ImageSerializer(data={"title": "t", "image": stub_image_upload()})
        self.assertFalse(serializer.is_valid())
        self.assertIn("owner", serializer.errors)

    def test_create_rejects_missing_image(self) -> None:
        owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        serializer = ImageSerializer(data={"title": "t", "owner": owner.pk})
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)

    def test_create_rejects_nonexistent_owner(self) -> None:
        serializer = ImageSerializer(
            data={"title": "t", "owner": 999_999, "image": stub_image_upload()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("owner", serializer.errors)

    def test_create_saves_image_to_storage(self) -> None:
        owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        upload = stub_image_upload("saved.png")
        serializer = ImageSerializer(
            data={"title": "Peak", "owner": owner.pk, "image": upload}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        instance.refresh_from_db()
        self.assertTrue(
            instance.image.name and instance.image.name.startswith("images/")
        )
        self.assertTrue(
            instance.image.name and instance.image.storage.exists(instance.image.name)
        )


class Share_LinkSerializerTests(TestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        self.image = Image.objects.create(
            title="i", owner=self.owner, image=stub_image_upload()
        )
        self.expiry = timezone.now()

    def test_serialize_outputs_expected_format(self) -> None:
        link = Share_Link.objects.create(image=self.image, expiry=self.expiry)
        data = Share_LinkSerializer(link).data
        expected_expiry = DRFSerializerDateTimeField().to_representation(link.expiry)
        self.assertEqual(
            data,
            {
                "id": link.pk,
                "image": self.image.pk,
                "expiry": expected_expiry,
            },
        )

    def test_create_rejects_missing_image(self) -> None:
        serializer = Share_LinkSerializer(
            data={
                "expiry": DRFSerializerDateTimeField().to_representation(self.expiry),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)

    def test_create_rejects_missing_expiry(self) -> None:
        serializer = Share_LinkSerializer(data={"image": self.image.pk})
        self.assertFalse(serializer.is_valid())
        self.assertIn("expiry", serializer.errors)

    def test_create_rejects_nonexistent_image(self) -> None:
        serializer = Share_LinkSerializer(
            data={
                "image": 999_999,
                "expiry": DRFSerializerDateTimeField().to_representation(self.expiry),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)

    def test_create_rejects_invalid_expiry(self) -> None:
        serializer = Share_LinkSerializer(
            data={"image": self.image.pk, "expiry": "not-a-datetime"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("expiry", serializer.errors)
