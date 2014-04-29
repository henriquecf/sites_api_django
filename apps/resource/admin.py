from django.contrib import admin

from apps.resource.models import User, Group, AuthorRestriction, Permission


admin.site.register(User)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(AuthorRestriction)