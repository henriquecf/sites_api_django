from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from owner.models import Owner


class Publication(Owner):
    """
    This model was intended to be inherited by every model that is publishable,
    can be published, unpublished, has an author, title and slug for the url
    """
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=150, editable=False)
    publication_start_date = models.DateTimeField(blank=True, default=timezone.now())
    publication_end_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, blank=True, related_name='author')

    def __str__(self):
        return self.title

    def publish(self):
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.now()
        if self.publication_end_date:
            self.publication_end_date = None
        self.save()
        return self.is_published()

    def unpublish(self):
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.now()
        self.publication_end_date = timezone.now()
        self.save()
        return self.is_published()

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


class Category(MPTTModel, Owner):
    """
    This model implements hierarchy.
    """
    name = models.CharField(max_length=150)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children_set')
    model_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'Categories'


def find_available_slug(model, instance, slug, original_slug, slug_number=2):
    """
    Recursive method that will add underscores to a slug field
    until a free value is located
    """
    try:
        sender_node = model.objects.get(slug=slug)
    except model.DoesNotExist:
        instance.slug = slug
    else:
        slug = slugify(original_slug + "-{0}".format(slug_number))
        slug_number += 1
        find_available_slug(model, instance, slug, original_slug, slug_number=slug_number)
    return