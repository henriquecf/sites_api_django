from django.db import models

from publication.models import Publication


class File(Publication):
    file = models.FileField(upload_to='files', blank=True)

    def __str__(self):
        if not self.file:
            return self.title
        return self.file.url
