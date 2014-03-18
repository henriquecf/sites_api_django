from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from accounts import views as account_views
from publication import views as publication_views
from news import views as news_views

admin.autodiscover()

router = DefaultRouter()
router.register(r'publication', publication_views.PublicationBaseViewSet)
router.register(r'category', news_views.CategoryBaseViewSet)
router.register(r'news', news_views.NewsViewSet)
router.register(r'account', account_views.AccountViewSet)

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include(router.urls), name='api'),
)
