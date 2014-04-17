from django.contrib import admin
from apps.resource.models import User, Group


admin.site.register(User)
admin.site.register(Group)