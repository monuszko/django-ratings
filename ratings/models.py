from __future__ import division, print_function
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from math import sqrt


class RatedObject(models.Model):
    """Provides methods for calculating scores of a rated object."""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

#    def get_ct(self):
#        """Returns the ContentType for this instance."""
#        return ContentType.objects.get_for_model(self)

    def get_scores(self):
        ct = ContentType.objects.get_for_model(self.content_object)
        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
        scores = [s.value for s in scores]

    def avg_score(self):
        scores = self.get_scores()
        return sum(scores) / len(scores)

    def std_deviation(self):
        """Returns average difference of ratings from the mean."""
        scores = self.get_scores()

        avg_score = self.avg_score()
        if not scores:
            return 0
        numerator = [pow((s - avg), 2) for s in scores]
        numerator = sum(numerator)
        return sqrt(numerator / len(ratings))


#class RatedModel(models.Model):
#    """All models with rating are meant to subclass this."""
#
#    def get_ct(self):
#        """Returns the ContentType for this instance."""
#        return ContentType.objects.get_for_model(self)
#
#    def get_scores(self):
#        ct = ContentType.objects.get_for_model(self)
#        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
#        scores = [s.value for s in scores]
#
#    def avg_score(self):
#        scores = self.get_scores()
#        return sum(scores) / len(scores)
#
#    def std_deviation(self):
#        """Returns average difference of ratings from the mean."""
#        scores = self.get_scores()
#
#        avg_score = self.avg_score()
#        if not scores:
#            return 0
#        numerator = [pow((s - avg), 2) for s in scores]
#        numerator = sum(numerator)
#        return sqrt(numerator / len(ratings))


#class Rating(models.Model):
#    """Represents a user's rating of an arbitrary object."""
#
#    def __repr__(self):
#        values = (self.content_type, self.object_id, self.user,
#                  self.opinion, self.pub_date)
#        return 'Rating({0}, {1}, {2}, {3}, {4})'.format(*values)
#
#    def __unicode__(self):
#        agg = self.aggregate_score()
#        subscores = []
#        for sc in self.subscores().items():
#            crit = sc[0]
#            val, mini, maxi = sc[1]
#            subscores.append('{0}: {1} in <{2}, {3}>'.format(crit, val, mini, maxi))
#        subscores = ', '.join(subscores)
#        return u"Rating: {0}, {{{1}}}".format(agg, subscores)
#
#
#    def subscores(self):
#        """Returns: {'criteria1': (value, min, max), ... }"""
#        result = dict()
#        scores = Score.objects.filter(rating=self.pk)
#        for sc in scores:
#            result[sc.criteria.name] = (sc.value, sc.criteria.range_min,
#                                        sc.criteria.range_max)
#        return result
#
#    class Meta:
#        unique_together = (('user', 'content_type', 'object_id'))


class Criteria(models.Model):
    """Scores must evaluate certain criteria. Criteria
    are specific to a given data model."""
    content_type = models.ForeignKey(ContentType)

    range_min = models.IntegerField()
    range_max = models.IntegerField()
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return u"Criteria {0} of {1}".format(self.name, self.content_type.model)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.range_min < self.range_max: 
            raise ValidationError("range_min must be lower than range_max!")

    class Meta:
        unique_together = (('name', 'content_type'))


class Opinion(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)
    opinion = models.TextField(blank=True)
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        return u"Opinion object for user {0}, ct {1}, obj_id {2}".format(
                self.user, self.content_type, self.object_id)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        # TODO: unique_together doesn't work here!

class Score(models.Model):
    """A generic score for any content object."""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)
    criteria = models.ForeignKey(Criteria)
    value = models.IntegerField()
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        val = str(self.value)
        model = self.content_type.model
        crit = self.criteria.name
        return u"Score: val {0}, model {1}, crit {2}".format(val, model, crit)

    def clean(self):
        from django.core.exceptions import ValidationError
        # I don't put it at the start of the file to play it safe (circular
        # imports). Squirrels report 'Django is notorious for circular imports'
        if not self.criteria.range_min <= self.value <= self.criteria.range_max:
            raise ValidationError("Score value not in Criteria's range!")
        if self.content_type != self.criteria.content_type:
            msg = "object's ContentType must match Criteria's ContentType!"
            raise ValidationError(msg)

    def normalized(self, newmin=0, newmax=10):
        """Return value normalized to another range"""
        oldmin = self.criteria.range_min
        oldmax = self.criteria.range_max

        oldspan = oldmax - oldmin
        newspan = newmax - newmin

        fraction = (self.value - oldmin) / oldspan
        return newmin + (fraction * newspan)


class TestDummy1(models.Model):
    pub_date = models.DateTimeField(default=now) 
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return u"TestDummy1: {}".format(self.title)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)


