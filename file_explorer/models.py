import os
from django.db import models
from category.models import Category

from publication.models import Publication
from settings.common_settings import MEDIA_ROOT


class File(Publication):
    """Hold file information about your location and your categories.

    The fields defined are:

    file - A path to the location of file.
    categories - A many to many relation with categories. It accepts null values.
    """
    file = models.FileField(upload_to=os.path.join(MEDIA_ROOT, 'files'))
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='files')

    def __str__(self):
        if not self.file:
            return self.title
        return self.file
