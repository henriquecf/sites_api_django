from django.db import models
from django.contrib.auth.models import User, Permission
from accounts.models import Account, Common


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