from django.contrib.auth import hashers
from rest_framework.viewsets import ModelViewSet

from .serializers import UserSerializer
from .models import User


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    filter_backends = ()

    def pre_save(self, obj):
        obj.parent = self.request.user
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)