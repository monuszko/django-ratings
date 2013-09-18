from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic


class Rating(models.Model):
    """A user rating not specific to any data model."""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    score = models.PositiveIntegerField()
    opinion = models.TextField(blank=True)


class Score(models.Model):
    """Several scores compose a Rating."""
    pass


class Criteria(models.Model):
    """Scores must evaluate certain criteria. Criteria
    are specific to a given data model."""
    pass


class TestDummy1(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)


