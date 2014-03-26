import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import AccountSerializer
from accounts.models import Account


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def pre_save(self, obj):
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        obj.owner = self.request.user