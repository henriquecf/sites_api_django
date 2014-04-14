from django.contrib import admin

from apps.account.models import Account, AccountUser, AccountGroup, CreatorRestriction


admin.site.register(Account)
admin.site.register(AccountUser)
admin.site.register(AccountGroup)
admin.site.register(CreatorRestriction)