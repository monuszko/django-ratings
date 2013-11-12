from __future__ import division, print_function
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from math import sqrt
from operator import itemgetter


def average(numbers):
    """Returns average of a sequence of numbers, or 0"""
    return sum(numbers) / len(numbers) if numbers else 0


class CriteriaManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return super(CriteriaManager, self).get_query_set().filter(
                publish=True,
                ).exclude(date_max__lt=now).exclude(date_min__gt=now)


class Criteria(models.Model):
    """Scores must evaluate certain criteria. Criteria
    are model-specific."""
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(max_length=250)

    # TODO: question folder using a "self" relation or M2M
    publish = models.BooleanField(default=True)
    date_min = models.DateTimeField(null=True, blank=True)
    date_max = models.DateTimeField(null=True, blank=True)
    public = CriteriaManager()
    objects = models.Manager()

    def __unicode__(self):
        return u"Criteria {0} of {1}".format(self.name,
                self.content_type.model)

    class Meta:
        unique_together = (('name', 'content_type'))


class Choice(models.Model):
    value = models.IntegerField()
    label = models.CharField(max_length=250)

    def __unicode__(self):
        return u"Choice: value '{}', label '{}'".format(self.value, self.label)

    class Meta:
        ordering = ['value']
        unique_together = ('value', 'label')


class Score(models.Model):
    """A generic score for any content object."""
    content_type = models.ForeignKey(ContentType, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, editable=False)
    criteria = models.ForeignKey(Criteria, editable=False)
    value = models.IntegerField()
    comment = models.CharField(blank=True, max_length=5000)
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        val = str(self.value)
        model = self.content_type.model
        crit = self.criteria.name
        return u"Score: val {0}, model {1}, crit {2}".format(val, model, crit)

    class Meta:
        unique_together = ('user', 'object_id', 'content_type', 'criteria')
        ordering = ['-pub_date']

