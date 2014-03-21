from django.contrib.auth import hashers
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, permissions
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User


class ChildrenRestriction(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_root_node():
            return obj in user.get_descendants()

        return obj == user


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    search_fields = ('username', 'email')
    filter_backends = (
        filters.SearchFilter,
    )
    permission_classes = (
        permissions.IsAuthenticated,
        ChildrenRestriction,
    )

    def get_queryset(self):
        user = self.request.user
        if user.is_root_node():
            # TODO Check if it is possible to use chain to retrieve user too
            #return list(chain(super(UserViewSet, self).get_queryset().filter(id=user.id), user.get_descendants()))
            return user.get_descendants()
        return super(UserViewSet, self).get_queryset().filter(id=user.id)

    def pre_save(self, obj):
        if self.request.method == 'POST':
            obj.parent = self.request.user
        if not hashers.is_password_usable(obj.password):
            obj.password = hashers.make_password(obj.password)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_root_node():
            return Response({'detail': 'You do not have permission to perform this action.'}, status=403)
        return super(UserViewSet, self).create(request, *args, **kwargs)