from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User, Permission


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
    global_permissions = models.ManyToManyField(Permission, null=True, blank=True)

    def has_global_permission(self, permission):
        """Checks if the user has global permission for that given permission."""
        return permission in set(
            "%s.%s" % (p.content_type.app_label, p.codename) for p in self.global_permissions.all())

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)