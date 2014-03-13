import datetime
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from account.models import Account
from account.serializers import AccountSerializer


class AccountBaseViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    model = Account

    def pre_save(self, obj):
        obj.owner = self.request.user
        obj.expiration_date = datetime.date.today() + datetime.timedelta(365)


class AccountViewSet(AccountBaseViewSet):
    permission_classes = (IsAdminUser, )