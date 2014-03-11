from django.db import models
from publication.models import Publication, Owner


# TODO Inherite from MPTTModel and implement parent with TreeForeignKey
class Category(Owner):
    name = models.CharField(max_length=150)


class News(Publication):
    content = models.TextField()
    #image = models.ImageField()
