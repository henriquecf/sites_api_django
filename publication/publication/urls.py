from django.conf.urls import patterns, url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from publication import views

admin.autodiscover()

router = DefaultRouter()
router.register(r'publication', views.PublicationViewSet)

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^publication/', include(router.urls), name='publication-list')
)
