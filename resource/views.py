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
from accounts.models import Account


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

    # TODO find a way to get account
    def pre_save(self, obj):
        obj.creator = self.request.user
        obj.account = Account.objects.get_or_create(id=1)[0]


class ResourceViewSet(ResourceBaseViewSet):
    filter_backends = (
        IsResourceFilterBackend,
        filters.SearchFilter,
    )


class ResourceChildrenViewSet(ResourceBaseViewSet):
    pass