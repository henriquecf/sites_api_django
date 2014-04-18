# -*- coding: utf-8 -*-

from datetime import date, timedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


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


class Account(Common):
    """Define personal account data for an user.

    This model saves data related to the account of a person.
    """
    expiration_date = models.DateField(_('expiration date'), editable=False, default=date.today() + timedelta(30))
    owner = models.OneToOneField(User, verbose_name=_('owner'), blank=True, related_name='account')

    def __str__(self):
        return self.owner.username

    class Meta(Common.Meta):
        verbose_name = _('account')
        verbose_name_plural = _('accounts')


