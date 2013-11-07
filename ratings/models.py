from __future__ import division, print_function
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from math import sqrt
from operator import itemgetter


def average(numbers):
    """Returns average of a sequence of numbers, or 0"""
    return sum(numbers) / len(numbers) if numbers else 0


class RatedObject(models.Model):
    """Provides methods for calculating scores of a rated object.  Serves as
    an intermediary between the actual rated object and its Score objects."""

    cached_avg = models.DecimalField(max_digits=2, decimal_places=1,
            default='0.0', editable=False)

#    def get_ct(self):
#        return ContentType.objects.get_for_model(self)
#
#    def get_forms(self, user):
#        from ratings.forms import ScoreForm # Circular import ;[
#        forms = []
#        ct = self.get_ct()
#        crits = self.get_ct().criteria_set.all()
#        for crit in crits:
#            forms.append(ScoreForm(prefix=crit.name, user=user, criteria=crit,
#                                   obj_id=self.pk))
#        return forms
#
#    def get_rate_url(self):
#        ct_id = self.get_ct().pk
#        obj_id = self.pk
#        return reverse('ratings:rate', kwargs={'ct_id': ct_id, 'obj_id': obj_id})
#
#    def get_crits(self):
#        ct = self.get_ct()
#        return Criteria.public.filter(content_type=ct)
#
#    def get_scores(self):
#        ct = self.get_ct()
#        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
#        scores = [s.value for s in scores]
#        return scores
#
#    def get_voters(self):
#        ct = self.get_ct()
#        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
#        voters = len({score.user for score in scores})
#        return voters
#
#    def avg_score(self):
#        scores = self.get_scores()
#        return sum(scores) / len(scores) if scores else 0
#
#    def scores_by_crit(self):
#        crits = self.get_crits()
#        result = []
#        for crit in crits:
#            scores = [sc.value for sc in Score.objects.filter(criteria=crit,
#                object_id=self.pk)]
#            avg = sum(scores) / len(scores) if scores else 0
#            # Calculate population standard deviation:
#            if not avg:
#                std_dev = 0
#            else:
#                numerator = sum(pow((s - avg), 2) for s in scores)
#                std_dev = sqrt(numerator / len(scores))
#            result.append({'name': crit.name, 'scores': scores, 'avg': avg,
#                           'std_dev': std_dev})
#        return result
#
#    def scores_by_users(self):
#        result = []
#        scores = Score.objects.filter(object_id=self.pk)
#        users = {}
#        for score in scores:
#            username = score.user.username
#            by_crit = {
#                    'name': score.criteria.name,
#                    'value': score.value,
#                    'comment': score.comment
#                    }
#            if username not in users:
#                users[username] = {
#                        'pub_date': score.pub_date,
#                        'by_crit' : [by_crit]
#                        }
#            else:
#                users[username]['by_crit'].append(by_crit)
#
#        for k, v in users.items():
#            numbers = [crit['value'] for crit in v['by_crit']]
#            avg = average(numbers)
#            by_crit = v['by_crit']
#            by_crit.sort(key=itemgetter('name'))
#            result.append(
#                    {
#                        'username': k,
#                        'pub_date': v['pub_date'],
#                        'by_crit': by_crit,
#                        'avg': avg
#                        }
#                    )
#        result.sort(key=itemgetter('pub_date'), reverse=True)
#        return result


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



