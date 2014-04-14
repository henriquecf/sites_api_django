from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from apps.resource.models import Resource


class Category(MPTTModel, Resource):
    """Model that will be related to any other that must be categorized.

    This model should just implement category to other models.
    Besides that, this categories can have hierarchy, being related to each other as parent or children.
    """
    name = models.CharField(_('name'), max_length=150)
    parent = TreeForeignKey('self', verbose_name=_('parent category'), null=True, blank=True, related_name='children_set')
    model_name = models.CharField(_('model name'), max_length=50)

    def __str__(self):
        return self.name

    class Meta(MPTTModel.Meta, Resource.Meta):
        verbose_name = _('category')
        verbose_name_plural = _('categories')