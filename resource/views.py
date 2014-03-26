from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.generic import FormView, CreateView
from rest_framework import viewsets
from rest_framework import filters
from resource.backends import IsResourceFilterBackend
from resource.forms import UserCreationFormWithEmail
from resource.models import Resource
from resource.serializers import ResourceSerializer


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


class ResourceBaseViewSet(viewsets.ModelViewSet):
    model = Resource
    serializer_class = ResourceSerializer


class ResourceViewSet(ResourceBaseViewSet):
    filter_backends = (
        IsResourceFilterBackend,
        filters.SearchFilter,
    )

    def pre_save(self, obj):
        obj.owner = self.request.user


class ResourceChildrenViewSet(ResourceBaseViewSet):

    def pre_save(self, obj):
        user = self.request.user
        if user.is_root_node():
            obj.owner = user
        else:
            obj.owner = user.get_root()
            obj.children = user