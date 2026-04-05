from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from backend.models import AccountTier, Image, Share_Link, User


class UserModelTests(TestCase):
    def test_name_accepts_max_length(self) -> None:
        user = User(name="x" * 255, account_tier=AccountTier.BASIC)
        user.full_clean()

    def test_name_rejects_over_max_length(self) -> None:
        user = User(name="x" * 256, account_tier=AccountTier.BASIC)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("name", ctx.exception.error_dict)

    def test_account_tier_accepts_basic(self) -> None:
        user = User(name="u", account_tier=AccountTier.BASIC)
        user.full_clean()

    def test_account_tier_accepts_premium(self) -> None:
        user = User(name="u", account_tier=AccountTier.PREMIUM)
        user.full_clean()

    def test_account_tier_accepts_enterprise(self) -> None:
        user = User(name="u", account_tier=AccountTier.ENTERPRISE)
        user.full_clean()

    def test_account_tier_rejects_invalid_choice(self) -> None:
        user = User(name="u", account_tier="Pro")
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("account_tier", ctx.exception.error_dict)

    def test_account_tier_rejects_over_max_length(self) -> None:
        user = User(name="u", account_tier="x" * 21)
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean()
        self.assertIn("account_tier", ctx.exception.error_dict)


class ImageModelTests(TestCase):
    def test_title_accepts_max_length(self) -> None:
        owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        image = Image(title="x" * 255, owner=owner)
        image.full_clean()

    def test_title_rejects_over_max_length(self) -> None:
        owner = User.objects.create(name="o", account_tier=AccountTier.BASIC)
        image = Image(title="x" * 256, owner=owner)
        with self.assertRaises(ValidationError) as ctx:
            image.full_clean()
        self.assertIn("title", ctx.exception.error_dict)


class DeletionCascadeTests(TestCase):
    def test_deleting_user_cascades_to_images(self) -> None:
        user = User.objects.create(name="u", account_tier=AccountTier.BASIC)
        image = Image.objects.create(title="t", owner=user)
        image_id = image.pk
        user.delete()
        self.assertFalse(Image.objects.filter(pk=image_id).exists())

    def test_deleting_user_cascades_to_share_links_via_image(self) -> None:
        user = User.objects.create(name="u", account_tier=AccountTier.BASIC)
        image = Image.objects.create(title="t", owner=user)
        link = Share_Link.objects.create(image=image, expiry=timezone.now())
        link_id = link.pk
        user.delete()
        self.assertFalse(Share_Link.objects.filter(pk=link_id).exists())

    def test_deleting_image_cascades_to_share_links(self) -> None:
        user = User.objects.create(name="u", account_tier=AccountTier.BASIC)
        image = Image.objects.create(title="t", owner=user)
        link = Share_Link.objects.create(image=image, expiry=timezone.now())
        link_id = link.pk
        image.delete()
        self.assertFalse(Share_Link.objects.filter(pk=link_id).exists())
