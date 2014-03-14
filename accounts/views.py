import datetime
from django.views.generic import CreateView, FormView
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from accounts.models import Account
from accounts.serializers import AccountSerializer
from accounts.forms import UserCreationFormWithEmail


class AccountBaseViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    model = Account

    def pre_save(self, obj):
        obj.owner = self.request.user
        obj.expiration_date = datetime.date.today() + datetime.timedelta(365)


class AccountViewSet(AccountBaseViewSet):
    permission_classes = (IsAdminUser, )


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationFormWithEmail
    template_name = 'accounts/form.html'
    success_url = '/'


class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/form.html'