import datetime
from rest_framework.viewsets import ModelViewSet
from .serializers import AccountSerializer
from accounts.models import Account


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer

    def pre_save(self, obj):
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        obj.owner = self.request.user