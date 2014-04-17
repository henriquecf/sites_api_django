from django.contrib import admin
from apps.resource.models import AccountUser, Group


admin.site.register(AccountUser)
admin.site.register(Group)