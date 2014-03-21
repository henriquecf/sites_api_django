import datetime

from accounts.models import Account
from owner.views import OwnerViewSet


class AccountViewSet(OwnerViewSet):
    model = Account

    def pre_save(self, obj):
        super(AccountViewSet, self).pre_save(obj)
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)