from django.contrib import admin

from .models import Publication, Category


admin.site.register(Publication)
admin.site.register(Category)