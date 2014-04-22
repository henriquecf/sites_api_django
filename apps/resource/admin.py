from django.contrib import admin
from apps.resource.models import User, Group, AuthorRestriction


admin.site.register(User)
admin.site.register(Group)
admin.site.register(AuthorRestriction)