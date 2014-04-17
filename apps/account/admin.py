from django.contrib import admin

from apps.account.models import Account, AuthorRestriction


admin.site.register(Account)
admin.site.register(AuthorRestriction)