import datetime
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from apps.resource.exceptions import BadRequestValidationError
from apps.account.serializers import (
    AccountSerializer,
)
from apps.account.models import Account


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        """Filter only user resources or get all if user is superuser."""
        return super(AccountViewSet, self).get_queryset().filter(owner=self.request.user)

    def pre_save(self, obj):
        """Create an account to a user only if he does not have one yet."""
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        try:
            Account.objects.get(owner=self.request.user)
            raise BadRequestValidationError(_('You already have an account and can not create another one.'))
        except ObjectDoesNotExist:
            obj.owner = self.request.user