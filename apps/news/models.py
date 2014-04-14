import os
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.category.models import Category
from apps.publication.models import Publication
from settings.common_settings import MEDIA_ROOT


class News(Publication):
    """Stores HTML content and an optional featured image, besides categories

    The fields defined here are:

    content - A text field that can contain HTML content;
    image - A path to the image location on the server. It accepts null valies;
    categories - A many to many relation with category model.
    """
    content = models.TextField(_('content'))
    image = models.ImageField(_('image'), upload_to=os.path.join(MEDIA_ROOT, 'files'), null=True, blank=True)
    categories = models.ManyToManyField(Category, verbose_name=_('categories'), null=True, blank=True,
                                        related_name='news')

    def __str__(self):
        return self.title

    class Meta(Publication.Meta):
        verbose_name = _('news')
        verbose_name_plural = _('tidings')