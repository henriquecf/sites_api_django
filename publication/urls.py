from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from account import views as account_views
from category.views import CategoryViewSet
from publication import views as publication_views
from news import views as news_views
from file_explorer import views as file_explorer_views
from newsletter import views as newsletter_views
from resource import views as resource_views


admin.autodiscover()

router = DefaultRouter()
router.register(r'publication', publication_views.PublicationBaseViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'news', news_views.NewsViewSet)
router.register(r'account', account_views.AccountViewSet)
router.register(r'file', file_explorer_views.FileViewSet)
router.register(r'subscription', newsletter_views.SubscriptionViewSet)
router.register(r'newsletter', newsletter_views.NewsletterViewSet)
router.register(r'submission', newsletter_views.SubmissionViewSet)
router.register(r'accountuser', account_views.AccountUserViewSet)
router.register(r'user', account_views.UserViewSet)
router.register(r'accountgroup', account_views.AccountGroupViewSet)
router.register(r'filterrestriction', account_views.FilterRestrictionViewSet)

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
                       url(r'^account/', include('account.urls')),
                       url(r'^permission/(?P<pk>[\d]+)/$', account_views.PermissionDetailView.as_view(),
                           name='permission-detail'),
                       url(r'^group/(?P<pk>[\d]+)/$', account_views.GroupDetailView.as_view(), name='group-detail'),
                       url(r'^site/(?P<pk>[\d]+)/$', resource_views.SiteRetrieveAPIView.as_view(), name='site-detail'),
                       url(r'^', include(router.urls), name='api'),
)
