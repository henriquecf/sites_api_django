from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from publication import views as publication_views
from news import views as news_views

admin.autodiscover()

router = DefaultRouter()
router.register(r'publication', publication_views.PublicationViewSet)
router.register(r'category', news_views.CategoryViewSet)

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(router.urls), name='api')
)
