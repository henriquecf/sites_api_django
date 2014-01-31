from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User


class Common(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_modification_date = models.DateTimeField(auto_now=True, editable=False)


class Publication(Common):
    title = models.CharField(max_length=150)
    description = models.TextField()
    slug = models.SlugField(max_length=150)
    publication_start_date = models.DateTimeField()
    publication_end_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, blank=True)

    def publish(self):
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.now()
        if self.publication_end_date:
            self.publication_end_date = None
        return True

    def is_published(self):
        if self.publication_end_date:
            if self.publication_start_date > timezone.now() or self.publication_end_date < timezone.now():
                return False
            else:
                return True
        elif self.publication_start_date > timezone.now():
            return False
        else:
            return True


def find_available_slug(object, instance, slug, original_slug, slug_number=2):
    """
    Recursive method that will add underscores to a slug field
    until a free value is located
    """
    try:
        sender_node = object.objects.get(slug=slug)
    except object.DoesNotExist:
        instance.slug = slug
    else:
        slug = slugify(original_slug + "-{0}".format(slug_number))
        slug_number += 1
        find_available_slug(object, instance, slug, original_slug, slug_number=slug_number)
    return


@receiver(pre_save, sender=Publication)
def slugify_title(sender, instance, *args, **kwargs):
    slug = slugify(instance.title)
    find_available_slug(sender, instance, slug, slug)