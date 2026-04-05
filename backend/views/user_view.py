from rest_framework import viewsets
from backend.models import User
from backend.serializer import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    serializer_class = UserSerializer
    queryset = User.objects.all()
