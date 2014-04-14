from django.contrib import admin

from apps.account.models import Account, AccountUser, AccountGroup, AuthorRestriction


admin.site.register(Account)
admin.site.register(AccountUser)
admin.site.register(AccountGroup)
admin.site.register(AuthorRestriction)