from django.conf.urls import patterns, url

from apps.resource.views import UserLoginView


urlpatterns = patterns('',
    url(r'^login/$', UserLoginView.as_view(), name='login'),
)