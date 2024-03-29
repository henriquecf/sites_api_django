# -*- coding: utf-8 -*-
from itertools import chain
from datetime import timedelta
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from apps.resource.models import Group, User as CustomUser, AuthorRestriction


class Fixtures:

    def __init__(self, test_case):
        self.test_case = test_case

    def create_owner_users(self):
        User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
        self.owner = User.objects.create_user('owner', 'owner@owner.com', '123')
        self.second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
        self.test_case.owner = self.owner
        self.test_case.second_owner = self.second_owner

    def create_owner_customusers(self):
        CustomUser.objects.create(owner=self.owner, user=self.owner, author=self.owner)
        CustomUser.objects.create(owner=self.second_owner, user=self.second_owner, author=self.second_owner)

    def create_users(self):
        self.owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
        self.owner_user2 = User.objects.create_user('owner_user2', 'owner_user2@owner.com', '123')
        CustomUser.objects.create(owner=self.owner, user=self.owner_user, author=self.owner)
        CustomUser.objects.create(owner=self.owner, user=self.owner_user2, author=self.owner)
        self.test_case.account_user = self.owner_user
        self.test_case.account_user2 = self.owner_user2

    def create_applications_and_tokens(self):
        self.owner_application = create_user_application(self.owner)
        self.second_owner_application = create_user_application(self.second_owner)
        self.test_case.owner_token = create_user_access_token(self.owner, self.owner_application)
        self.test_case.second_owner_token = create_user_access_token(self.second_owner, self.second_owner_application)
        self.test_case.account_user_token = create_user_access_token(self.owner_user, self.owner_application)
        self.test_case.account_user_token2 = create_user_access_token(self.owner_user2, self.owner_application)


def create_user_access_token(user, application):
    return AccessToken.objects.create(user=user, token=user.username,
                                      application=application,
                                      expires=timezone.now() + timedelta(30)).token


def create_user_application(user):
    return Application.objects.create(user=user, client_type='confidential',
                                      authorization_grant_type='password')


def user_accountuser_account_token_fixture(test_case):
    fixture = Fixtures(test_case)
    fixture.create_owner_users()
    fixture.create_owner_customusers()
    fixture.create_users()
    fixture.create_applications_and_tokens()
    return fixture


def user_accountuser_account_permissions_token_fixture(test_case):
    fixture = user_accountuser_account_token_fixture(test_case)
    # TODO Take care of permissions dependencies between models.
    # TODO Model inheritance must include permission inheritance.
    permissions = Permission.objects.filter(codename__endswith=test_case.model._meta.model_name)
    pub_permissions = Permission.objects.filter(codename__endswith='publication')
    cat_permissions = Permission.objects.filter(codename__endswith='category')
    for permission in chain(permissions, pub_permissions, cat_permissions):
        test_case.owner.user_permissions.add(permission)
        test_case.second_owner.user_permissions.add(permission)
        test_case.account_user2.user_permissions.add(permission)
        AuthorRestriction.objects.create(permission=permission, user=test_case.account_user2, owner=test_case.owner,
                                         filter_values='{0},{1}'.format(test_case.account_user2.id,
                                                                        test_case.owner.id), author=test_case.owner)
    test_accountgroup = Group.objects.create(role='Test Group', owner=fixture.owner, author=test_case.owner)
    test_case.owner.groups.add(test_accountgroup.group)


def user_token_fixture(test_case):
    fixture = Fixtures(test_case)
    fixture.create_owner_users()
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = create_user_application(fixture.owner)
    second_owner_application = create_user_application(fixture.second_owner)
    test_case.owner_token = create_user_access_token(fixture.owner, owner_application)
    test_case.second_owner_token = create_user_access_token(fixture.second_owner, second_owner_application)
    test_case.account_user_token = create_user_access_token(owner_user, owner_application)


def user_account_token_fixture(test_case):
    fixture = Fixtures(test_case)
    fixture.create_owner_users()
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = create_user_application(fixture.owner)
    second_owner_application = create_user_application(fixture.second_owner)
    test_case.owner_token = create_user_access_token(fixture.owner, owner_application)
    test_case.second_owner_token = create_user_access_token(fixture.second_owner, second_owner_application)
    test_case.account_user_token = create_user_access_token(owner_user, owner_application)