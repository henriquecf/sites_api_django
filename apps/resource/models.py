from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models

from apps.account.models import Account, Common


class AccountSite(Common):
    account = models.ForeignKey(Account, verbose_name=_('account'), editable=False)
    site = models.ForeignKey(Site, verbose_name=_('site'))

    def __str__(self):
        return self.site.domain

    class Meta(Common.Meta):
        unique_together = ['account', 'site']
        verbose_name = _('account site')
        verbose_name_plural = _('account sites')


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    account = models.ForeignKey(Account, verbose_name=_('account'), editable=False)
    creator = models.ForeignKey(User, verbose_name=_('creator'), editable=False, related_name='creators')
    sites = models.ManyToManyField(AccountSite, verbose_name=_('sites'), blank=True)

    def account_sites(self):
        return self.sites.filter(account=self.account)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.creator)

    class Meta(Common.Meta):
        verbose_name = _('resource')
        verbose_name_plural = _('resources')