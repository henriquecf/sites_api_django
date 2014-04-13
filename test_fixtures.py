# -*- coding: utf-8 -*-
from itertools import chain
from datetime import timedelta
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from apps.account.models import AccountUser, Account, FilterRestriction, AccountGroup


def create_owner_users():
    User.objects.create_superuser('henrique', 'elo.henrique@gmail.com', '123')
    owner = User.objects.create_user('owner', 'owner@owner.com', '123')
    owner.is_staff = True
    owner.save()
    second_owner = User.objects.create_user('second_owner', 'second_owner@owner.com', '123')
    second_owner.is_staff = True
    second_owner.save()
    return owner, second_owner


def create_owner_accounts(owner, second_owner):
    owner_account = Account.objects.create(owner=owner)
    second_owner_account = Account.objects.create(owner=second_owner)
    return owner_account, second_owner_account


def create_owner_accountusers(owner, second_owner, owner_account, second_owner_account):
    AccountUser.objects.create(account=owner_account, user=owner)
    AccountUser.objects.create(account=second_owner_account, user=second_owner)


def create_account_users(owner_account):
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_user2 = User.objects.create_user('owner_user2', 'owner_user2@owner.com', '123')
    AccountUser.objects.create(account=owner_account, user=owner_user)
    AccountUser.objects.create(account=owner_account, user=owner_user2)
    return owner_user, owner_user2


def create_user_access_token(user, application):
    return AccessToken.objects.create(user=user, token=user.username,
                                      application=application,
                                      expires=timezone.now() + timedelta(30)).token


def create_user_application(user):
    return Application.objects.create(user=user, client_type='confidential',
                                      authorization_grant_type='password')


def create_applications_and_tokens(test_case, owner, second_owner, owner_user, owner_user2):
    owner_application = create_user_application(owner)
    second_owner_application = create_user_application(second_owner)
    test_case.owner_token = create_user_access_token(owner, owner_application)
    test_case.second_owner_token = create_user_access_token(second_owner, second_owner_application)
    test_case.account_user_token = create_user_access_token(owner_user, owner_application)
    test_case.account_user_token2 = create_user_access_token(owner_user2, owner_application)


def user_accountuser_account_permissions_token_fixture(test_case):
    owner, second_owner = create_owner_users()
    owner_account, second_owner_account = create_owner_accounts(owner, second_owner)
    create_owner_accountusers(owner, second_owner, owner_account, second_owner_account)
    owner_user, owner_user2 = create_account_users(owner_account)
    create_applications_and_tokens(test_case, owner, second_owner, owner_user, owner_user2)
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
        FilterRestriction.objects.create(permission=permission,
                                         user=test_case.account_user2,
                                         filter_field='creator',
                                         values='{0},{1}'.format(test_case.account_user2.id,
                                                                 test_case.owner.id))
    test_accountgroup = AccountGroup.objects.create(role='Test Group', account=owner_account)
    test_case.owner.groups.add(test_accountgroup.group)


def user_token_fixture(test_case):
    owner, second_owner = create_owner_users()
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = create_user_application(owner)
    second_owner_application = create_user_application(second_owner)
    test_case.owner_token = create_user_access_token(owner, owner_application)
    test_case.second_owner_token = create_user_access_token(second_owner, second_owner_application)
    test_case.account_user_token = create_user_access_token(owner_user, owner_application)


def user_account_token_fixture(test_case):
    owner, second_owner = create_owner_users()
    owner_account, second_owner_account = create_owner_accounts(owner, second_owner)
    owner_user = User.objects.create_user('owner_user', 'owner_user@owner.com', '123')
    owner_application = create_user_application(owner)
    second_owner_application = create_user_application(second_owner)
    test_case.owner_token = create_user_access_token(owner, owner_application)
    test_case.second_owner_token = create_user_access_token(second_owner, second_owner_application)
    test_case.account_user_token = create_user_access_token(owner_user, owner_application)


def user_accountuser_account_token_fixture(test_case):
    owner, second_owner = create_owner_users()
    owner_account, second_owner_account = create_owner_accounts(owner, second_owner)
    create_owner_accountusers(owner, second_owner, owner_account, second_owner_account)
    owner_user, owner_user2 = create_account_users(owner_account)
    create_applications_and_tokens(test_case, owner, second_owner, owner_user, owner_user2)
    test_case.owner = owner
    test_case.second_owner = second_owner
    test_case.account_user = owner_user
    test_case.account_user2 = owner_user2