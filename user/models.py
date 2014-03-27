from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account, Common


class AccountUser(Common):
    user = models.OneToOneField(User, blank=True)
    account = models.ForeignKey(Account, blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)