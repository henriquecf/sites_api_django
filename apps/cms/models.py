# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from apps.category.models import Category
from apps.publication.models import Publication


class Page(Publication):
    category = models.OneToOneField(Category, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            self.category
        except Category.DoesNotExist:
            self.category = Category.objects.create(name=self.slug, author=self.author, owner=self.owner,
                                                    model=ContentType.objects.get_for_model(Page))
        super(Page, self).save()

    class Meta(Publication.Meta):
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')


class Module(Publication):
    model = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    model_object = GenericForeignKey('model', 'object_id')
    filters = models.TextField(blank=True)
    page = models.ManyToManyField(Page, related_name='modules')
    position = models.CharField(max_length=4, choices=(
        ('1', _('Top')), ('2', _('Left')), ('3', _('Center')), ('4', _('Right')), ('5', _('Bottom'))))
    order = models.IntegerField()
