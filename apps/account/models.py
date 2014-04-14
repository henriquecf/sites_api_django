from datetime import date, timedelta
from django.db import models
from django.db.utils import IntegrityError
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


class AccountGroup(Common):
    group = models.OneToOneField(Group, blank=True)
    role = models.CharField(max_length=100)
    account = models.ForeignKey(Account, blank=True)

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


class AccountUser(Common):
    user = models.OneToOneField(User, blank=True)
    account = models.ForeignKey(Account, blank=True)

    def __str__(self):
        return '{0} - {1}'.format(self.account, self.user)


class CreatorRestriction(models.Model):
    filter_values = models.TextField()
    permission = models.ForeignKey(Permission)
    user = models.ForeignKey(User, null=True, blank=True, related_name='creator_restrictions')
    group = models.ForeignKey(Group, null=True, blank=True, related_name='creator_restrictions')

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
        super(CreatorRestriction, self).save()

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
        super(CreatorRestriction, self).delete()

    def __str__(self):
        if self.user:
            user_or_group = self.user
        else:
            user_or_group = self.group
        return '{0} - {1} - {2} - {3}'.format(user_or_group, self.permission, self.filter_field, self.values)

