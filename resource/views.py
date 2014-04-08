from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site, get_current_site
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework import viewsets, permissions
from rest_framework.generics import RetrieveAPIView
from resource.models import Resource
from resource.serializers import ResourceSerializer, SiteSerializer


class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'accounts/form.html'

    def get_success_url(self):
        """Checks if there is a URL to redirect through the key "next". Goes to root URL otherwise."""
        try:
            return self.request.GET['next']
        except KeyError:
            return '/'

    def form_valid(self, form):
        """Authenticates the user and logs him in."""
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(UserLoginView, self).form_valid(form)


class ResourceViewSet(viewsets.ModelViewSet):
    model = Resource
    serializer_class = ResourceSerializer

    def pre_save(self, obj):
        """Checks if there is a creator and account for the resource.

        Does nothing if it has, assigns the request user and its account to the object otherwise.
        """
        try:
            obj.creator
            obj.account
        except ObjectDoesNotExist:
            obj.creator = self.request.user
            obj.account = self.request.user.accountuser.account

    def post_save(self, obj, created=False):
        if not obj.sites.all():
            domain = self.request.META.get('SERVER_NAME')
            site, created = Site.objects.get_or_create(domain=domain)
            obj.sites.add(site)


class SiteRetrieveAPIView(RetrieveAPIView):
    model = Site
    serializer_class = SiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()