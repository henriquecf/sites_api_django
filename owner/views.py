from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.generic import FormView, CreateView
from rest_framework import viewsets

from owner.forms import UserCreationFormWithEmail
from owner.models import Owner
from owner.serializers import OwnerSerializer


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


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationFormWithEmail
    template_name = 'accounts/form.html'
    success_url = '/'


class OwnerViewSet(viewsets.ModelViewSet):
    serializer_class = OwnerSerializer
    model = Owner

    def pre_save(self, obj):
        obj.owner = self.request.user