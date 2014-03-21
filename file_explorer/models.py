from django.db import models

from publication.models import Publication, Category


class File(Publication):
    # TODO Find a way to test post file. This field must not be blank
    file = models.FileField(upload_to='files', blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True, related_name='files')

    def __str__(self):
        if not self.file:
            return self.title
        return self.file
