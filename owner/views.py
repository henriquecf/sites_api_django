from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.generic import FormView, CreateView
from rest_framework import viewsets
from rest_framework import filters
from owner.backends import IsOwnerFilterBackend
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


class OwnerBaseViewSet(viewsets.ModelViewSet):
    model = Owner
    serializer_class = OwnerSerializer


class OwnerViewSet(OwnerBaseViewSet):
    filter_backends = (
        IsOwnerFilterBackend,
        filters.SearchFilter,
    )

    def pre_save(self, obj):
        obj.owner = self.request.user


class OwnerChildrenViewSet(OwnerBaseViewSet):

    def pre_save(self, obj):
        user = self.request.user
        if user.is_root_node():
            obj.owner = user
        else:
            obj.owner = user.get_root()
            obj.children = user