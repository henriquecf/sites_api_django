from django.db import models

from publication.models import Publication, Category


class News(Publication):
    """Stores HTML content and an optional featured image, besides categories

    The fields defined here are:

    content - A text field that can contain HTML content;
    image - A path to the image location on the server. It accepts null valies;
    categories - A many to many relation with category model.
    """
    content = models.TextField()
    image = models.ImageField(upload_to='media/news/', null=True, blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='news')

    def __str__(self):
        return self.title