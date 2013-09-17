from django.db import models

from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic


class RatedItem(models.Model):
    score = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class TestDummy(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
