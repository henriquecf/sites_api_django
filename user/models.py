from django.contrib.auth.models import User
import mptt
from mptt.fields import TreeForeignKey

# add a parent foreign key
TreeForeignKey(User, blank=True, null=True).contribute_to_class(User, 'parent')

mptt.register(User, order_insertion_by=['username'])
