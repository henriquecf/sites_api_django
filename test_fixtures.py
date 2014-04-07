# -*- coding: utf-8 -*-
from itertools import chain
from datetime import timedelta
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from account.models import AccountUser, Account, FilterPermission


def user_accountuser_account_token_fixture(test_case):
    User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
    owner = User.objects.create_user('owner', 'owner@owner.com', '123')
    owner.is_staff = True
    owner.save()
    second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
    second_owner.is_staff = True
    second_owner.save()
    owner_account = Account.objects.create(owner=owner)
    second_owner_account = Account.objects.create(owner=second_owner)
    AccountUser.objects.create(account=owner_account, user=owner)
    AccountUser.objects.create(account=second_owner_account, user=second_owner)
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_user2 = User.objects.create_user('owner_user2', 'owner_user2@owner.com', '123')
    AccountUser.objects.create(account=owner_account, user=owner_user)
    AccountUser.objects.create(account=owner_account, user=owner_user2)
    owner_application = Application.objects.create(user=owner, client_type='confidential',
                                                   authorization_grant_type='password')
    second_owner_application = Application.objects.create(user=second_owner, client_type='confidential',
                                                          authorization_grant_type='password')
    test_case.owner_token = AccessToken.objects.create(user=owner, token=owner.username, application=owner_application,
                                                       expires=timezone.now() + timedelta(30)).token
    test_case.second_owner_token = AccessToken.objects.create(user=second_owner, token=second_owner.username,
                                                              application=second_owner_application,
                                                              expires=timezone.now() + timedelta(30)).token
    test_case.account_user_token = AccessToken.objects.create(user=owner_user, token=owner_user.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token
    test_case.account_user_token2 = AccessToken.objects.create(user=owner_user2,
                                                               token=owner_user2.username,
                                                               application=owner_application,
                                                               expires=timezone.now() + timedelta(30)).token
    test_case.owner = owner
    test_case.second_owner = second_owner
    test_case.account_user = owner_user
    test_case.account_user2 = owner_user2
    # TODO Take care of permissions dependencies between models.
    # TODO Model inheritance must include permission inheritance.
    permissions = Permission.objects.filter(codename__endswith=test_case.model._meta.model_name)
    pub_permissions = Permission.objects.filter(codename__endswith='publication')
    cat_permissions = Permission.objects.filter(codename__endswith='category')
    for permission in chain(permissions, pub_permissions, cat_permissions):
        test_case.owner.user_permissions.add(permission)
        test_case.second_owner.user_permissions.add(permission)
        test_case.account_user2.user_permissions.add(permission)
        filter_permission = FilterPermission.objects.create(permission=permission,
                                                            account_user=test_case.account_user2.accountuser,
                                                            filter_field='creator',
                                                            values='{0}'.format(test_case.account_user2.id))


def user_token_fixture(test_case):
    User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
    owner = User.objects.create_user('owner', 'owner@owner.com', '123')
    owner.is_staff = True
    owner.save()
    second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
    second_owner.is_staff = True
    second_owner.save()
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = Application.objects.create(user=owner, client_type='confidential',
                                                   authorization_grant_type='password')
    second_owner_application = Application.objects.create(user=second_owner, client_type='confidential',
                                                          authorization_grant_type='password')
    test_case.owner_token = AccessToken.objects.create(user=owner, token=owner.username, application=owner_application,
                                                       expires=timezone.now() + timedelta(30)).token
    test_case.second_owner_token = AccessToken.objects.create(user=second_owner, token=second_owner.username,
                                                              application=second_owner_application,
                                                              expires=timezone.now() + timedelta(30)).token
    test_case.account_user_token = AccessToken.objects.create(user=owner_user, token=owner_user.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token


def user_account_token_fixture(test_case):
    User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
    owner = User.objects.create_user('owner', 'owner@owner.com', '123')
    owner.is_staff = True
    owner.save()
    second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
    second_owner.is_staff = True
    second_owner.save()
    owner_account = Account.objects.create(owner=owner)
    second_owner_account = Account.objects.create(owner=second_owner)
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = Application.objects.create(user=owner, client_type='confidential',
                                                   authorization_grant_type='password')
    second_owner_application = Application.objects.create(user=second_owner, client_type='confidential',
                                                          authorization_grant_type='password')
    test_case.owner_token = AccessToken.objects.create(user=owner, token=owner.username, application=owner_application,
                                                       expires=timezone.now() + timedelta(30)).token
    test_case.second_owner_token = AccessToken.objects.create(user=second_owner, token=second_owner.username,
                                                              application=second_owner_application,
                                                              expires=timezone.now() + timedelta(30)).token
    test_case.account_user_token = AccessToken.objects.create(user=owner_user, token=owner_user.username,
                                                              application=owner_application,
                                                              expires=timezone.now() + timedelta(30)).token