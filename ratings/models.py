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


class RatedModel(models.Model):
    """Provides methods for calculating scores of a rated object."""
    cached_avg = models.DecimalField(max_digits=2, decimal_places=1,
            default='0.0', editable=False)

    def get_ct(self):
        return ContentType.objects.get_for_model(self)

    def get_forms(self, user):
        forms = []
        ct = self.get_ct()
        crits = self.get_ct().criteria_set.all()
        for crit in crits:
            forms.append(ScoreForm(prefix=crit.name, user=user, criteria=crit,
                                   obj_id=self.pk))
        return forms

    def get_rate_url(self):
        ct_id = self.get_ct().pk
        obj_id = self.pk
        return reverse('ratings:rate', kwargs={'ct_id': ct_id, 'obj_id': obj_id})

    def get_crits(self):
        ct = self.get_ct()
        return Criteria.objects.filter(content_type=ct)

    def get_scores(self):
        ct = self.get_ct()
        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
        scores = [s.value for s in scores]
        return scores

    def get_voters(self):
        ct = self.get_ct()
        scores = Score.objects.filter(content_type=ct, object_id=self.pk)
        voters = len({score.user for score in scores})
        return voters

    def avg_score(self):
        scores = self.get_scores()
        return sum(scores) / len(scores) if scores else 0

    def scores_by_crit(self):
        crits = self.get_crits()
        result = []
        for crit in crits:
            scores = [sc.value for sc in Score.objects.filter(criteria=crit,
                object_id=self.pk)]
            avg = sum(scores) / len(scores) if scores else 0
            # Calculate population standard deviation:
            if not avg:
                std_dev = 0
            else:
                numerator = sum(pow((s - avg), 2) for s in scores)
                std_dev = sqrt(numerator / len(scores))
            result.append({'name': crit.name, 'scores': scores, 'avg': avg,
                           'std_dev': std_dev})
        return result

    def scores_by_users(self):
        result = []
        scores = Score.objects.filter(object_id=self.pk)
        users = {}
        for score in scores:
            username = score.user.username
            if username not in users:
                by_crit = [
                        {
                        'name': score.criteria.name,
                        'value': score.value,
                        'comment': score.comment
                        }
                    ]
                users[username] = {
                        'pub_date': score.pub_date,
                        'by_crit' : by_crit
                        }
            else:
                users[username]['by_crit'].append(
                        {
                            'name': score.criteria.name,
                            'value': score.value,
                            'comment': score.comment
                        }
                    )

        print('USERS!!!', users)
        for k, v in users.items():
            numbers = [crit['value'] for crit in v['by_crit']]
            print('Print 2')
            print('numbers for average', numbers)
            avg = average(numbers)
            by_crit = v['by_crit']
            by_crit.sort(key=itemgetter('name'))
            result.append(
                    {
                        'username': k,
                        'pub_date': v['pub_date'],
                        'by_crit': by_crit,
                        'avg': avg
                        }
                    )
        result.sort(key=itemgetter('pub_date'), reverse=True)
        print('result !!!!!!!!!!!!!', result)
        return result

    def std_dev(self):
        """Returns average difference of Scores from the mean."""
        # TODO: Make this User-based rather than Score-based
        scores = self.get_scores()

        avg_score = self.avg_score()
        if not scores:
            return 0
        numerator = [pow((s - avg_score), 2) for s in scores]
        numerator = sum(numerator)
        return sqrt(numerator / len(scores))


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
        if not self.val_min < self.val_max: 
            raise ValidationError("val_min must be lower than val_max!")

    class Meta:
        unique_together = (('name', 'content_type'))


class Score(models.Model):
    """A generic score for any content object."""
    content_type = models.ForeignKey(ContentType, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, editable=False)
    criteria = models.ForeignKey(Criteria, editable=False)
    # TODO: values in Score instead of Criteria ? Hmm.
    VALUE_CHOICES = (
            (1, '1-Very poor!'),
            (2, '2-Poor'),
            (3, '3-Average'),
            (4, '4-Good'),
            (5, '5-Very good!'),
            )
    value = models.IntegerField(choices=VALUE_CHOICES)
    comment = models.CharField(blank=True, max_length=5000)
    pub_date = models.DateTimeField(default=now, editable=False) 

    def __unicode__(self):
        val = str(self.value)
        model = self.content_type.model
        crit = self.criteria.name
        return u"Score: val {0}, model {1}, crit {2}".format(val, model, crit)

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
        ordering = ['-pub_date']


class ScoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.criteria = kwargs.pop('criteria', None)
        self.obj_id = kwargs.pop('obj_id', None)
        super(ScoreForm, self).__init__(*args, **kwargs)

    def min(self):
        return self.criteria.val_min
    def max(self):
        return self.criteria.val_max
    def name(self):
        return self.criteria.name

    def clean(self):
        cleaned_data = super(ScoreForm, self).clean()
        value = cleaned_data['value'] 
        vmin, vmax = self.criteria.val_min, self.criteria.val_max
        if not vmin <= value <= vmax:
            raise ValidationError("Score value not in Criteria's range! {} {} {}".format(vmin, value, vmax))
        if Score.objects.filter(user=self.user,
                                object_id=self.obj_id,
                                content_type=self.criteria.content_type,
                                criteria=self.criteria).exists():
            raise ValidationError("Only one Score per User per object!")
        return cleaned_data

    class Meta:
        model = Score
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
                }

