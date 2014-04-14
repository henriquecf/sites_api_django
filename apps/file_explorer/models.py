import os
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.category.models import Category
from apps.publication.models import Publication
from settings.common import MEDIA_ROOT


class File(Publication):
    """Hold file information about your location and your categories.

    The fields defined are:

    file - A path to the location of file.
    categories - A many to many relation with categories. It accepts null values.
    """
    file = models.FileField(_('file'), upload_to=os.path.join(MEDIA_ROOT, 'files'))
    categories = models.ManyToManyField(Category, verbose_name=_('categories'), null=True, blank=True,
                                        related_name='files')

    def __str__(self):
        if not self.file:
            return self.title
        return self.file

    class Meta(Publication.Meta):
        verbose_name = _('file')
        verbose_name_plural = _('files')