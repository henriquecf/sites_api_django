# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.db import models
from apps.publication.models import Publication


class Page(Publication):

    class Meta(Publication.Meta):
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
