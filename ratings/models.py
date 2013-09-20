from __future__ import division
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now


class Rating(models.Model):
    """A user rating not specific to any data model."""
    content_type = models.ForeignKey(ContentType)
    # TODO: restrict Rating to data models (admin interface...)
    # TODO: related objects (admin interface...)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)
    opinion = models.TextField(blank=True)
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        return u"Rating: user {0}, obj {1}, model {2}".format(
                self.user.username, self.object_id, self.content_type.model)

    def aggregate_score(self):
        """The average of user's sub-scores"""
        # TODO: Cache score to save lookup time
        scores = Score.objects.filter(rating=self.pk)
        return sum(Score.normalized() for sc in scores) / len(scores)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'))


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


class Score(models.Model):
    """Several scores compose a Rating."""
    rating = models.ForeignKey(Rating)
    criteria = models.ForeignKey(Criteria)
    value = models.IntegerField()

    def __unicode__(self):
        return u"Score: val {0}, model {1}, crit {2}".format(
                self.value, self.rating.content_type.model, self.criteria.name)

    def clean(self):
        from django.core.exceptions import ValidationError
        # I don't put it at the start of the file to play it safe (circular
        # imports). Squirrels report 'Django is notorious for circular imports'
        if not self.criteria.range_min <= self.value <= self.criteria.range_max:
            raise ValidationError("Score value not in Criteria's range!")
        if self.criteria.content_type != self.rating.content_type:
            msg = "Rating's ContentType doesn't match Criteria's ContentType!"
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
    pub_date = models.DateTimeField(default=now, editable=False) 
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)


