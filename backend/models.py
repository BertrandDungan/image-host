from django.db import models

MAX_STRING_LENGTH = 255


class AccountTier(models.TextChoices):
    BASIC = "Basic"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"


class User(models.Model):
    name = models.CharField(max_length=MAX_STRING_LENGTH)
    account_tier = models.CharField(
        max_length=20,
        choices=AccountTier.choices,
    )


class Image(models.Model):
    title = models.CharField(max_length=MAX_STRING_LENGTH)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")


class Share_Link(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expiry = models.DateTimeField()
