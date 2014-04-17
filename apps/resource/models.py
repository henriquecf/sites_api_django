from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.contrib.auth.models import User, Group
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
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False, related_name='authors')
    sites = models.ManyToManyField(AccountSite, verbose_name=_('sites'), blank=True)

    def account_sites(self):
        return self.sites.filter(account=self.account)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.author)

    class Meta(Common.Meta):
        verbose_name = _('resource')
        verbose_name_plural = _('resources')


class AccountGroup(Common):
    group = models.OneToOneField(Group, verbose_name=_('group'), blank=True)
    role = models.CharField(_('role'), max_length=100)
    account = models.ForeignKey(Account, verbose_name=_('account'), blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        name = '{0} - {1}'.format(self.account, self.role)
        self.group = Group.objects.get_or_create(name=name)[0]
        super(AccountGroup, self).save()

    def delete(self, using=None):
        self.group.delete()
        super(AccountGroup, self).delete()

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.role)

    class Meta(Common.Meta):
        verbose_name = _('account group')
        verbose_name_plural = _('account groups')


class AccountUser(Common):
    user = models.OneToOneField(User, verbose_name=_('user'), blank=True)
    account = models.ForeignKey(Account, verbose_name=_('account'), blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)

    class Meta(Common.Meta):
        verbose_name = _('account user')
        verbose_name_plural = _('account users')