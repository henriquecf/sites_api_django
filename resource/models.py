from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models

from account.models import Account, Common


class AccountSite(Common):
    account = models.ForeignKey(Account, editable=False)
    site = models.ForeignKey(Site)

    def __str__(self):
        return self.site.domain

    class Meta:
        unique_together = ['account', 'site']


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    account = models.ForeignKey(Account, editable=False)
    creator = models.ForeignKey(User, editable=False, related_name='creators')
    sites = models.ManyToManyField(AccountSite, blank=True)

    def account_sites(self):
        return self.sites.filter(account=self.account)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.creator)