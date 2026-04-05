from django.db import models


class AccountTier(models.TextChoices):
    BASIC = "Basic"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"


class User(models.Model):
    name = models.CharField(max_length=255)
    account_tier = models.CharField(
        max_length=20,
        choices=AccountTier.choices,
    )


class Image(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Share_Link(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expiry = models.DateTimeField()
