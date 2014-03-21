# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'password']