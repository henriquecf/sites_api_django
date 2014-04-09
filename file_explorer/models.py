from django.db import models
from category.models import Category

from publication.models import Publication


class File(Publication):
    """Hold file information about your location and your categories.

    The fields defined are:

    file - A path to the location of file.
    categories - A many to many relation with categories. It accepts null values.
    """
    # TODO Find a way to test post file. This field must not be blank
    file = models.FileField(upload_to='media/files', default='media/files/image.png')
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='files')

    def __str__(self):
        if not self.file:
            return self.title
        return self.file
