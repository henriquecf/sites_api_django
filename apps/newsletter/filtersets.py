# -*- coding: utf-8 -*-
from apps.publication.filtersets import PublicationFilterSet
from apps.newsletter.models import Newsletter


class NewsletterFilterSet(PublicationFilterSet):

    class Meta(PublicationFilterSet.Meta):
        model = Newsletter