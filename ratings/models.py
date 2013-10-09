from __future__ import division, print_function
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from math import sqrt


class RatedModel(models.Model):
    """Provides methods for calculating scores of a rated object."""
    cached_avg = models.DecimalField(max_digits=2, decimal_places=1, default='0.0')

    def get_scores(self):
        ct = ContentType.objects.get_for_model(self)
        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
        scores = [s.value for s in scores]

    def avg_score(self):
        scores = self.get_scores()
        return sum(scores) / len(scores)

    def std_dev(self):
        """Returns average difference of ratings from the mean."""
        scores = self.get_scores()

        avg_score = self.avg_score()
        if not scores:
            return 0
        numerator = [pow((s - avg), 2) for s in scores]
        numerator = sum(numerator)
        return sqrt(numerator / len(ratings))

    def subscores(self):
        """Returns: {'criteria1': (value, min, max), ... }"""
        result = dict()
        scores = Score.objects.filter(rating=self.pk)
        for sc in scores:
            result[sc.criteria.name] = (sc.value, sc.criteria.val_min,
                    sc.criteria.val_max)


class Criteria(models.Model):
    """Scores must evaluate certain criteria. Criteria
    are model-specific."""
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(max_length=250)

    val_min = models.IntegerField()
    val_max = models.IntegerField()
    labels = models.CharField(blank=True, max_length=250) # json

    #folder = ForeignKey # relacja self np Null raczej M2M
    published = models.BooleanField(default=True)
    date_min = models.DateTimeField(null=True, blank=True)
    date_max = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u"Criteria {0} of {1} <{2}-{3}>".format(self.name,
                self.content_type.model, self.val_min, self.val_max)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.val_min < self.val_max: 
            raise ValidationError("val_min must be lower than val_max!")

    class Meta:
        unique_together = (('name', 'content_type'))


class Score(models.Model):
    """A generic score for any content object."""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User)
    criteria = models.ForeignKey(Criteria)
    value = models.IntegerField()
    comment = models.CharField(max_length=5000)
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        val = str(self.value)
        model = self.content_type.model
        crit = self.criteria.name
        return u"Score: val {0}, model {1}, crit {2}".format(val, model, crit)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.criteria.val_min <= self.value <= self.criteria.val_max:
            raise ValidationError("Score value not in Criteria's range!")
        ct = self.content_type if hasattr(self, 'content_type') else None
        # HACK: apparently Model.clean() is called twice, the first time
        # Score.content_type doesn't exist, the second time it does.
        # Also a hack for bug #12028 (unique_together vs obj.content_type)
        if Score.objects.filter(user=self.user,
                                object_id=self.object_id,
                                content_type=ct,
                                criteria=self.criteria).exists():
            raise ValidationError("Only one Score per User per object!")

    def normalized(self, newmin=0, newmax=10):
        """Return value normalized to another range"""
        oldmin = self.criteria.val_min
        oldmax = self.criteria.val_max

        oldspan = oldmax - oldmin
        newspan = newmax - newmin

        fraction = (self.value - oldmin) / oldspan
        return newmin + (fraction * newspan)

    class Meta:
        unique_together = ('user', 'object_id', 'content_type', 'criteria')


class TestDummy1(RatedModel):
    pub_date = models.DateTimeField(default=now) 
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return u"TestDummy1: {}".format(self.title)

class TestDummy2(RatedModel):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)

class TestDummy2(RatedModel):
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True)


