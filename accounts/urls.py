from django.conf.urls import patterns, url

from resource.views import UserLoginView, UserCreateView


urlpatterns = patterns('',

    url(r'^user/create/', UserCreateView.as_view(), name='user-create'),
    url(r'^login/$', UserLoginView.as_view(), name='login'),
)