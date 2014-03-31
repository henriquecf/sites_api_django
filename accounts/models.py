from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User


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


class Account(Common):
    """Define personal account data for an user.

    This model saves data related to the account of a person.
    """
    expiration_date = models.DateField(editable=False)
    owner = models.OneToOneField(User, editable=False, related_name='account')

    def __str__(self):
        return self.owner.username