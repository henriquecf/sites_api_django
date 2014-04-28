# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.http import HttpRequest
from apps.resource.models import AuthUser, User, Site, ContribSite, AuthorRestriction, Permission
from apps.resource.backends import SiteDomainFilterBackend, AuthorRestrictionBackend, ResourceFilterBackend, \
    custom_permissions_map
from apps.news.models import News
from apps.news.views import NewsViewSet


class BackendsTestCase(LiveServerTestCase):
    def setUp(self):
        user = AuthUser.objects.create_user(username='user', password='123')
        User.objects.create(user=user, author=user, owner=user)
        request = HttpRequest()
        request.user = user
        self.request = request
        news = News.objects.create(owner=user, author=user, title='News')
        site = ContribSite.objects.create(domain='testserver')
        Site.objects.create(owner=user, author=user, site=site)
        news.sites.add(site)
        self.user = user
        self.news_queryset = News.objects.all()

    def test_site_domain_filter_backend(self):
        self.request.META['HTTP_HOST'] = 'testserver'
        backend = SiteDomainFilterBackend()
        self.assertEqual(1, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(sites__domain='testserver')),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))
        self.request.META['HTTP_HOST'] = 'otherserver'
        self.assertEqual(0, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(sites__domain='otherserver')),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))
        self.request.META['HTTP_HOST'] = None
        self.request.META['SERVER_NAME'] = 'testserver'
        self.assertEqual(1, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(sites__domain='testserver')),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))
        self.request.META['SERVER_NAME'] = 'otherserver'
        self.assertEqual(0, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(sites__domain='otherserver')),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))

    def test_resource_filter_backend(self):
        backend = ResourceFilterBackend()
        self.assertEqual(1, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(owner=self.request.user.user.owner)),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))
        other_user = AuthUser.objects.create_user(username='other_user', password='123')
        User.objects.create(owner=other_user, author=other_user, user=other_user)
        self.request.user = other_user
        self.assertEqual(0, backend.filter_queryset(self.request, self.news_queryset, view=None).count())
        self.assertEqual(list(News.objects.filter(owner=self.request.user.user.owner)),
                         list(backend.filter_queryset(self.request, self.news_queryset, view=None)))

    def test_author_restriction_backend(self):
        self.request.method = 'GET'
        perm = Permission.objects.filter(codename__endswith='news').all()[3]
        author_restriction = AuthorRestriction.objects.create(owner=self.user, author=self.user, user=self.user,
                                                              permission=perm,
                                                              filter_values='2')
        backend = AuthorRestrictionBackend()
        queryset = backend.filter_queryset(self.request, self.news_queryset, view=NewsViewSet)
        self.assertEqual(0, queryset.count())
        author_restriction.filter_values = self.user.id
        author_restriction.save()
        queryset = backend.filter_queryset(self.request, self.news_queryset, view=NewsViewSet)
        self.assertEqual(1, queryset.count())
        author_restriction.filter_values = '2'
        author_restriction.save()
        queryset = backend.filter_queryset(self.request, self.news_queryset, view=NewsViewSet)
        self.assertEqual(0, queryset.count())
        author_restriction.delete()
        queryset = backend.filter_queryset(self.request, self.news_queryset, view=NewsViewSet)
        self.assertEqual(1, queryset.count())

    def test_custom_permissions_map(self):
        custom_perms_map = {}

        for method in custom_permissions_map.keys():
            custom_perms_map[method] = []
            values = custom_permissions_map[method]
            for value in values:
                custom_perms_map[method].extend([value % {'app_label': 'news', 'model_name': 'news'}])

        self.assertEqual(custom_perms_map['GET'], ['news.view_news'])
        self.assertEqual(custom_perms_map['OPTIONS'], [])
        self.assertEqual(custom_perms_map['HEAD'], [])
        self.assertEqual(custom_perms_map['POST'], ['news.add_news'])
        self.assertEqual(custom_perms_map['PUT'], ['news.change_news'])
        self.assertEqual(custom_perms_map['PATCH'], ['news.change_news'])
        self.assertEqual(custom_perms_map['DELETE'], ['news.delete_news'])