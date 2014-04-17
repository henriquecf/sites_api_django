from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup
from django.contrib.sites.models import Site
from django.db import models

from apps.account.models import Account, Common


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    account = models.ForeignKey(Account, verbose_name=_('account'), editable=False)
    author = models.ForeignKey(AuthUser, verbose_name=_('author'), editable=False, related_name='authors')
    sites = models.ManyToManyField(Site, verbose_name=_('sites'), blank=True)

    def account_sites(self):
        return self.sites.filter(account=self.account)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.author)

    class Meta(Common.Meta):
        verbose_name = _('resource')
        verbose_name_plural = _('resources')


class Group(Resource):
    group = models.OneToOneField(AuthGroup, verbose_name=_('group'), blank=True)
    role = models.CharField(_('role'), max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        name = '{0} - {1}'.format(self.account, self.role)
        self.group = AuthGroup.objects.get_or_create(name=name)[0]
        super(Group, self).save()

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.role)

    class Meta(Common.Meta):
        verbose_name = _('group')
        verbose_name_plural = _('groups')


class AccountUser(Common):
    user = models.OneToOneField(AuthUser, verbose_name=_('user'), blank=True)
    account = models.ForeignKey(Account, verbose_name=_('account'), blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)

    class Meta(Common.Meta):
        verbose_name = _('account user')
        verbose_name_plural = _('account users')


class AccountSite(Common):
    account = models.ForeignKey(Account, verbose_name=_('account'), editable=False)
    site = models.ForeignKey(Site, verbose_name=_('site'))

    def __str__(self):
        return self.site.domain

    class Meta(Common.Meta):
        unique_together = ['account', 'site']
        verbose_name = _('account site')
        verbose_name_plural = _('account sites')

# TODO rename accountuser to user and inherit from resource
# TODO Remove User API
# TODO rename AccountSite to Site and inherit from Resource
# TODO move AuthorRestriction to Resource app
# TODO move backends, login and exceptions and urls to resource
# TODO Remove account app