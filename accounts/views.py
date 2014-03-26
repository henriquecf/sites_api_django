import datetime

from accounts.models import Account
from resource.views import ResourceChildrenViewSet


class AccountViewSet(ResourceChildrenViewSet):
    model = Account

    def pre_save(self, obj):
        super(AccountViewSet, self).pre_save(obj)
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)