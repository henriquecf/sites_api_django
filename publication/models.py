from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from resource.models import Resource


class Publication(Resource):
    """Anything that will be published in a site.

    This model is the base for any other model that will be used as a publication in a site.
    It has basic publications functionality and can be used by its own, or inherited by other models.
    """
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=150, editable=False)
    publication_start_date = models.DateTimeField(blank=True, default=timezone.now())
    publication_end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def publish(self):
        """Publishes a publication.

        Sets the publication start date to now, if it is bigger than now, and sets the publication end date to None.
        Returns the state of the publication.
        """
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.now()
        if self.publication_end_date:
            self.publication_end_date = None
        self.save()
        return self.is_published()

    def unpublish(self):
        """Unpublishes the publication.

        Sets the publication start date to now, if it is bigger than now, and sets the publication end date also to now.
        Returns the state of the publication.
        """
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.now()
        self.publication_end_date = timezone.now()
        self.save()
        return self.is_published()

    def is_published(self):
        """Returns True if the publication is published or False otherwise."""
        if self.publication_end_date:
            if self.publication_start_date > timezone.now() or self.publication_end_date < timezone.now():
                return False
            else:
                return True
        elif self.publication_start_date > timezone.now():
            return False
        else:
            return True


class Category(MPTTModel, Resource):
    """Model that will be related to any other that must be categorized.

    This model should just implement category to other models.
    Besides that, this categories can have hierarchy, being related to each other as parent or children.
    """
    name = models.CharField(max_length=150)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children_set')
    model_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


def find_available_slug(model, instance, slug, original_slug, slug_number=2):
    #Adds underscores with an incrementing number to the slug until an available one is found.
    try:
        sender_node = model.objects.get(slug=slug)
    except model.DoesNotExist:
        instance.slug = slug
    else:
        slug = slugify(original_slug + "-{0}".format(slug_number))
        slug_number += 1
        find_available_slug(model, instance, slug, original_slug, slug_number=slug_number)
    return