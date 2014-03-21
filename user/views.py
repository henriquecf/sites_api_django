from itertools import chain
from django.contrib.auth import hashers
from django.forms.models import model_to_dict
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, permissions
from rest_framework.response import Response

from .serializers import UserSerializer, UserCreateChangeSerializer
from .models import User


class ChildrenRestriction(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_root_node():
            return obj == user or obj in user.get_descendants()

        return obj == user


class UserViewSet(ModelViewSet):
    model = User
    search_fields = ('username', 'email')
    filter_backends = (
        filters.SearchFilter,
    )
    permission_classes = (
        permissions.IsAuthenticated,
        ChildrenRestriction,
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return UserCreateChangeSerializer

    def pre_save(self, obj):
        if self.request.method == 'POST':
            obj.parent = self.request.user
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_root_node():
            return Response({u'detail': u'You do not have permission to perform this action.'}, status=403)
        return super(UserViewSet, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not request.user.is_root_node():
            return Response(data={u'detail': u'You do not have permission to perform this action.'}, status=403)
        return super(UserViewSet, self).list(request, *args, **kwargs)