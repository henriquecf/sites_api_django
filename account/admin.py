from django.contrib import admin
from .models import Account, AccountUser


admin.site.register(Account)
admin.site.register(AccountUser)