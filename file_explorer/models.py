from django.db import models

from publication.models import Publication, Category


class File(Publication):
    file = models.FileField(upload_to='files', blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='files')

    def __str__(self):
        if not self.file:
            return self.title
        return self.file
