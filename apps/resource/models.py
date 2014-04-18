from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, Permission
from django.contrib.sites.models import Site as ContribSite
from django.db import models, IntegrityError


class Common(models.Model):
    """Encapsulate creation and modification dates for all models.

    This is an abstract class that defines common fields for models.
    The two fields defined are:

    creation_date - automatically defined when object is created;
    last_modification_date - automatically actualized when object is saved.
    """
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    last_modification_date = models.DateTimeField(_('last modification date'), auto_now=True)

    class Meta:
        abstract = True
        default_permissions = ('view', 'add', 'change', 'delete')


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    owner = models.ForeignKey(AuthUser, verbose_name=_('owner'), editable=False)
    author = models.ForeignKey(AuthUser, verbose_name=_('author'), editable=False, related_name='authors')
    sites = models.ManyToManyField(ContribSite, verbose_name=_('sites'), blank=True)

    def account_sites(self):
        return self.sites.filter(owner=self.owner)

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.author)

    class Meta(Common.Meta):
        verbose_name = _('resource')
        verbose_name_plural = _('resources')


class Group(Resource):
    group = models.OneToOneField(AuthGroup, verbose_name=_('group'), blank=True)
    role = models.CharField(_('role'), max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        name = '{0} - {1}'.format(self.owner, self.role)
        self.group = AuthGroup.objects.get_or_create(name=name)[0]
        super(Group, self).save()

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.role)

    class Meta(Common.Meta):
        verbose_name = _('group')
        verbose_name_plural = _('groups')


class User(Resource):
    user = models.OneToOneField(AuthUser, verbose_name=_('user'), blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.user)

    class Meta(Common.Meta):
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Site(Resource):
    site = models.ForeignKey(ContribSite, verbose_name=_('site'))

    def __str__(self):
        return self.site.domain

    class Meta(Common.Meta):
        verbose_name = _('site')
        verbose_name_plural = _('sites')


class AuthorRestriction(Common):
    filter_values = models.TextField(_('filter values'))
    permission = models.ForeignKey(Permission, verbose_name=_('permission'))
    user = models.ForeignKey(AuthUser, verbose_name=_('user'), null=True, blank=True,
                             related_name='creator_restrictions')
    group = models.ForeignKey(AuthGroup, verbose_name=_('group'), null=True, blank=True,
                              related_name='creator_restrictions')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.user:
            try:
                self.user.user_permissions.add(self.permission)
            except IntegrityError:
                pass
        elif self.group:
            try:
                self.group.permissions.add(self.permission)
            except IntegrityError:
                pass
        super(AuthorRestriction, self).save()

    def delete(self, using=None):
        if self.user:
            try:
                self.user.user_permissions.remove(self.permission)
            except IntegrityError:
                pass
        elif self.group:
            try:
                self.group.permissions.remove(self.permission)
            except IntegrityError:
                pass
        super(AuthorRestriction, self).delete()

    def __str__(self):
        if self.user:
            user_or_group = self.user
        else:
            user_or_group = self.group
        return '{0} - {1} - {2}'.format(user_or_group, self.permission, self.filter_values)

    class Meta(Common.Meta):
        verbose_name = _('author restriction')
        verbose_name_plural = _('author restrictions')


# TODO Remove account app
# TODO Revise serializers, viewsets and models. Remove unecessary stuff. Nest serializers.
# TODO redo translation