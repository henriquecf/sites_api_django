from django.contrib import admin

from .models import Submission, Subscription, Newsletter


admin.site.register(Subscription)
admin.site.register(Submission)
admin.site.register(Newsletter)