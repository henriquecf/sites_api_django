from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models


class Common(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)


class Owner(Common):
    owner = models.ForeignKey(User, blank=True)


class Account(Owner):
    expiration_date = models.DateField(editable=False, default=datetime.today()+timedelta(30))