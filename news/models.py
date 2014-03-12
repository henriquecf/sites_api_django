from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from publication.models import Publication, Owner


class Category(MPTTModel, Owner):
    name = models.CharField(max_length=150)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class News(Publication):
    content = models.TextField()
    #image = models.ImageField()
