from django.contrib.auth import hashers
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from .serializers import UserSerializer
from .models import User


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    search_fields = ('username', 'email')
    filter_backends = (
        filters.SearchFilter,
    )

    def pre_save(self, obj):
        obj.parent = self.request.user
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)