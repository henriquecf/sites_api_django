from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.views.generic import FormView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.resource.models import Resource, AccountSite
from apps.resource.serializers import ResourceSerializer, AccountSiteSerializer


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
        """Checks if there is a author and account for the resource.

        Does nothing if it has, assigns the request user and its account to the object otherwise.
        """
        try:
            obj.author
            obj.account
        except ObjectDoesNotExist:
            obj.author = self.request.user
            obj.account = self.request.user.accountuser.account

    def post_save(self, obj, created=False):
        if not obj.sites.all():
            domain = self.request.META.get('HTTP_HOST')
            if not domain:
                domain = self.request.META.get('SERVER_NAME')
            site, created = Site.objects.get_or_create(domain=domain)
            account_site, created2 = AccountSite.objects.get_or_create(site=site, account=obj.account)
            obj.sites.add(account_site)


class AccountSiteRetrieveAPIViewSet(ReadOnlyModelViewSet):
    model = AccountSite
    serializer_class = AccountSiteSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    filter_backends = ()

    def get_queryset(self):
        return super(AccountSiteRetrieveAPIViewSet, self).get_queryset().filter(
            account=self.request.user.accountuser.account)