from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

class Publication(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.SlugField(max_length=150)
    publication_start_date = models.DateTimeField()
    publication_end_date = models.DateTimeField(blank=True, null=True)


@receiver(pre_save, sender=Publication)
def slugify_title(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)