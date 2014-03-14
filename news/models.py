from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from accounts.models import Account
from publication.models import Publication


class Category(MPTTModel, Account):
    name = models.CharField(max_length=150)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class News(Publication):
    content = models.TextField()
    image = models.ImageField(upload_to='media/news/', null=True, blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='news_set')

    def __str__(self):
        return self.title