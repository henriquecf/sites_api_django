from django.contrib import admin
from apps.resource.models import AccountUser, AccountGroup


admin.site.register(AccountUser)
admin.site.register(AccountGroup)