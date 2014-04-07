from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User, Permission, Group


class Common(models.Model):
    """Encapsulate creation and modification dates for all models.

    This is an abstract class that defines common fields for models.
    The two fields defined are:

    creation_date - automatically defined when object is created;
    last_modification_date - automatically actualized when object is saved.
    """
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        default_permissions = ('view', 'add', 'change', 'delete')


class Account(Common):
    """Define personal account data for an user.

    This model saves data related to the account of a person.
    """
    expiration_date = models.DateField(editable=False, default=date.today()+timedelta(30))
    owner = models.OneToOneField(User, blank=True, related_name='account')

    def __str__(self):
        return self.owner.username


class AccountUser(Common):
    user = models.OneToOneField(User, blank=True)
    account = models.ForeignKey(Account, blank=True)
    filter_permissions = models.ManyToManyField(Permission, through='FilterRestriction', null=True, blank=True)

    def has_filter_permission(self, permission):
        """Checks if the user has global permission for that given permission."""
        return permission in set(
            "%s.%s" % (p.content_type.app_label, p.codename) for p in self.filter_permissions.all())

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)


class FilterRestriction(models.Model):
    filter_field = models.CharField(max_length=100)
    values = models.TextField()
    permission = models.ForeignKey(Permission)
    account_user = models.ForeignKey(AccountUser)

    def __str__(self):
        return '{0} - {1} - {2} - {3}'.format(self.account_user, self.permission, self.filter_field, self.values)

    class Meta:
        pass#unique_together = ['filter_field', 'permission', 'account_user']


class AccountGroup(Group):
    role = models.CharField(max_length=100)
    account = models.ForeignKey(Account, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = '{0}-{1}'.format(self.account, self.role)
        super(AccountGroup, self).save()

    def __str__(self):
        return '{0}-{1}'.format(self.account, self.role)

