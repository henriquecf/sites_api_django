from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from apps.resource.models import Resource


class Publication(Resource):
    """Anything that will be published in a site.

    This model is the base for any other model that will be used as a publication in a site.
    It has basic publications functionality and can be used by its own, or inherited by other models.
    """
    title = models.CharField(_('title'), max_length=150)
    content = models.TextField(_('content'), blank=True)
    description = models.TextField(_('description'), blank=True)
    slug = models.SlugField(_('slug'), max_length=150, editable=False)
    publication_start_date = models.DateTimeField(_('publication start date'), blank=True, default=timezone.now())
    publication_end_date = models.DateTimeField(_('publication end date'), blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.publication_start_date:
            if timezone.is_naive(self.publication_start_date):
                timezone.make_aware(self.publication_start_date, timezone.get_current_timezone())
        if self.publication_end_date:
            if timezone.is_naive(self.publication_end_date):
                timezone.make_aware(self.publication_end_date, timezone.get_current_timezone())
        super(Publication, self).save()

    def __str__(self):
        return self.title

    def publish(self):
        """Publishes a publication.

        Sets the publication start date to now, if it is bigger than now, and sets the publication end date to None.
        Returns the state of the publication.
        """
        if self.publication_start_date > timezone.now():
            self.publication_start_date = timezone.datetime.now()
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
            self.publication_start_date = timezone.datetime.now()
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

    class Meta(Resource.Meta):
        verbose_name = _('publication')
        verbose_name_plural = _('publications')


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