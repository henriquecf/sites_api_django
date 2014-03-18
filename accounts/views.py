import datetime
from django.views.generic import CreateView, FormView
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from accounts.models import Owner, Account
from accounts.serializers import OwnerSerializer
from accounts.forms import UserCreationFormWithEmail


class OwnerViewSet(viewsets.ModelViewSet):
    serializer_class = OwnerSerializer
    model = Owner

    def pre_save(self, obj):
        obj.owner = self.request.user


class AccountViewSet(OwnerViewSet):
    permission_classes = (IsAdminUser, )
    model = Account

    def pre_save(self, obj):
        super(AccountViewSet, self).pre_save(obj)
        obj.expiration_date = datetime.date.today() + datetime.timedelta(30)


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationFormWithEmail
    template_name = 'accounts/form.html'
    success_url = '/'


class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/form.html'

    def get_success_url(self):
        try:
            return self.request.GET['next']
        except:
            return '/'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(UserLoginView, self).form_valid(form)