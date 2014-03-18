from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from accounts.models import Owner
from publication.models import Publication


class Category(MPTTModel, Owner):
    """
    This model implements hierarchy.
    """
    name = models.CharField(max_length=150)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class News(Publication):
    """
    Stores HTML content and an optional featured image, besides categories
    """
    # TODO The content must be stored in HTML mode
    content = models.TextField()
    image = models.ImageField(upload_to='media/news/', null=True, blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='news_set')

    def __str__(self):
        return self.title