from django.contrib.auth.models import User
from django.db import models

from account.models import Account, Common


class Resource(Common):
    """
    The resource class, together with its serializer and viewset,
    are the base of any api that can be accessed just by its resource.
    To use this behavior, the application must inherit the model,
    serializer and viewset
    """
    account = models.ForeignKey(Account, editable=False)
    creator = models.ForeignKey(User, editable=False, related_name='creators')

    def __str__(self):
        return self.creator.username