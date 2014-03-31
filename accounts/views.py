import datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import AccountSerializer
from accounts.models import Account
from user.exceptions import OwnerValidationError


class AccountViewSet(ModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    filter_backends = ()

    def get_queryset(self):
        """Filter only user resources or get all if user is superuser."""
        if self.request.user.is_superuser:
            return super(AccountViewSet, self).get_queryset()
        else:
            return super(AccountViewSet, self).get_queryset().filter(owner=self.request.user)

    def pre_save(self, obj):
        """Create an account to a user only if he does not have one yet."""
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)
        try:
            Account.objects.get(owner=self.request.user)
            raise OwnerValidationError('You already have an account and can not create another one.')
        except ObjectDoesNotExist:
            obj.owner = self.request.user