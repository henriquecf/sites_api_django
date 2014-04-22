from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from apps.category.views import CategoryViewSet
from apps.news import views as news_views
from apps.publication import views as publication_views
from apps.file_explorer import views as file_explorer_views
from apps.newsletter import views as newsletter_views
from apps.resource.views import UserViewSet, GroupViewSet, AuthorRestrictionViewSet, PermissionViewSet


admin.autodiscover()

router = DefaultRouter()
router.register(r'publication', publication_views.PublicationBaseViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'news', news_views.NewsViewSet)
router.register(r'permission', PermissionViewSet)
router.register(r'file', file_explorer_views.FileViewSet)
router.register(r'subscription', newsletter_views.SubscriptionViewSet)
router.register(r'newsletter', newsletter_views.NewsletterViewSet)
router.register(r'submission', newsletter_views.SubmissionViewSet)
router.register(r'user', UserViewSet)
router.register(r'group', GroupViewSet)
router.register(r'authorrestriction', AuthorRestrictionViewSet)

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
                       url(r'^accounts/', include('apps.resource.urls')),
                       url(r'^', include(router.urls), name='api'),
)
