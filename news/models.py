from django.db import models

from publication.models import Publication, Category


class News(Publication):
    """
    Stores HTML content and an optional featured image, besides categories
    """
    content = models.TextField()
    image = models.ImageField(upload_to='media/news/', null=True, blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='news_set')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = u'News'