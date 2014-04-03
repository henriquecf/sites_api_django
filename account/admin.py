from django.contrib import admin
from .models import Account, AccountUser, AccountGroup


admin.site.register(Account)
admin.site.register(AccountUser)
admin.site.register(AccountGroup)