from django.contrib.auth.models import User
from django.db import models


class Common(models.Model):
    """
    Fields that must be in all models
    """
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    owner = models.ForeignKey(User, blank=True, related_name='owners')
    children = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        if self.children:
            return self.children.username
        return self.owner.username

    class Meta:
        permissions = (
            ('read_resource', 'Can read resource'),
            ('read_global_resource', 'Can read all resources'),
            ('add_global_resource', 'Can add all resources'),
            ('change_global_resource', 'Can change all resources'),
            ('delete_global_resource', 'Can delete all resources'),
        )