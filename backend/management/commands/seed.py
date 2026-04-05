from django.core.management.base import BaseCommand

from backend.models import AccountTier, User


SEED_USERS: list[tuple[str, AccountTier]] = [
    ("Bobby", AccountTier.BASIC),
    ("Penny", AccountTier.PREMIUM),
    ("Eddy", AccountTier.ENTERPRISE),
]


class Command(BaseCommand):
    help = "Create sample User rows (one per account tier)."

    def handle(self, *args: None, **options: None) -> None:
        created = 0
        for name, tier in SEED_USERS:
            _, was_created = User.objects.get_or_create(
                name=name,
                defaults={"account_tier": tier},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created user: {name} ({tier})"))
            else:
                self.stdout.write(f"Skipped (already exists): {name}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created} new user(s)."))
