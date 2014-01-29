from django.db import models


class Publication(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.CharField(max_length=150)
    publication_start_date = models.DateTimeField()
    publication_end_date = models.DateTimeField(blank=True, null=True)