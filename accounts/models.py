from django.contrib.auth.models import User
from django.db import models


class Common(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)


class Account(Common):
    owner = models.ForeignKey(User, blank=True, related_name='owner2')
    expiration_date = models.DateField(editable=False)