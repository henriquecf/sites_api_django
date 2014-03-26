from django.contrib.auth import hashers
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, permissions
from accounts.models import Account

from .serializers import AccountUserSerializer
from .models import AccountUser


# TODO Refactor this viewset to filter by users related to that account
class AccountUserViewSet(ModelViewSet):
    model = AccountUser
    permission_classes = (
        permissions.IsAdminUser,
    )
    serializer_class = AccountUserSerializer

    # TODO insert account of the owner and get right user
    def pre_save(self, obj):
        obj.account = self.request.user.account
        obj.user = self.request.user
        print(self.request.user, obj.account, obj.user)