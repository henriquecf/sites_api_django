# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apps.category.models import Category
from apps.publication.models import Publication


class Page(Publication):
    category = models.OneToOneField(Category, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        page_content_type = ContentType.objects.get_for_model(Page)
        try:
            self.category = Category.objects.get(name=self.slug, author=self.author, owner=self.owner,
                                                 model=page_content_type)
        except Category.DoesNotExist:
            self.category = Category.objects.create(name=self.slug, author=self.author, owner=self.owner,
                                                    model=page_content_type)
        super(Page, self).save()

    class Meta(Publication.Meta):
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
