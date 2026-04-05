from django.db.models import QuerySet
from rest_framework import viewsets

from backend.models import User
from backend.serializer import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.all()
