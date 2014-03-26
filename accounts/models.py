from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User


class Common(models.Model):
    """
    Fields that must be in all models
    """
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Account(Common):
    """
    This model must save any data related to the account of a person,
    including payment data, signature date controls, contact fields
    needed for payment, etc
    """
    expiration_date = models.DateField(editable=False, default=datetime.today()+timedelta(30))
    owner = models.OneToOneField(User, blank=True, related_name='account')
    # TODO include is owner filter

    def __str__(self):
        return self.owner.username