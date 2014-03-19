# -*- coding: utf-8 -*-
from publication.filtersets import PublicationFilterSet
from .models import Newsletter


class NewsletterFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Newsletter