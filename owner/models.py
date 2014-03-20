# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Common(models.Model):
    """
    Fields that must be in all models
    """
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)


class Owner(Common):
    """
    The owner class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its owner.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    owner = models.ForeignKey(User, blank=True)

    def __str__(self):
        return self.owner.username

    class Meta:
        verbose_name_plural = u'Owners'