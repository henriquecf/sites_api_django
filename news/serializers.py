from rest_framework import serializers
from publication.serializers import OwnerSerializer
from .models import Category


class CategorySerializer(OwnerSerializer):

    class Meta:
        model = Category