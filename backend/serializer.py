from rest_framework import serializers
from backend.models import User, Image, Share_Link


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "name", "account_tier"]


class ImageSerializer(serializers.ModelSerializer[Image]):
    class Meta:
        model = Image
        fields = ["id", "title", "owner"]


class Share_LinkSerializer(serializers.ModelSerializer[Share_Link]):
    class Meta:
        model = Share_Link
        fields = ["id", "image", "expiry"]
