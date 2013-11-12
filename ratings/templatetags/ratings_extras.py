from __future__ import division
from math import sqrt
from operator import itemgetter
from django import template
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from ratings.models import Score, Criteria
from ratings.forms import ScoreForm

register = template.Library()

def average(numbers):
    """Returns average of a sequence of numbers, or 0"""
    return sum(numbers) / len(numbers) if numbers else 0

class ListRating:
    """Provides methods for displaying ratings in list views."""
    def __init__(self, ratedobject):
        self.ratedobject = ratedobject

    def _get_ct(self):
        return ContentType.objects.get_for_model(self.ratedobject)

    def _get_scores(self):
        ct = self._get_ct()
        scores = User.objects.filter(
                score__content_type=ct,
                score__object_id=self.ratedobject.pk).values(
                        'username').annotate(average_rating=Avg('score__value'))
        scores = [row['average_rating'] for row in scores
                if row['average_rating']]
        return scores

    def avg_score(self):
        scores = self._get_scores()
        return sum(scores) / len(scores) if scores else 0

    def std_dev(self):
        scores = self._get_scores()
        avg = self.avg_score()
        if not avg:
            return 0
        else:
            numerator = sum(pow((s - avg), 2) for s in scores)
            return sqrt(numerator / len(scores))

    def num_voters(self):
        ct = self._get_ct()
        scores = Score.objects.filter(content_type=ct, object_id=self.ratedobject.pk)
        voters = len({score.user for score in scores})
        return voters


class DetailRating(ListRating):
    """Provides methods for displaying ratings in detail views."""
    def __init__(self, ratedobject, user):
        self.ratedobject = ratedobject
        self.user = user

    def get_forms(self):
        #from ratings.forms import ScoreForm # Circular import ;[
        forms = []
        ct = self._get_ct()
        crits = self._get_ct().criteria_set.all()
        for crit in crits:
            forms.append(ScoreForm(prefix=crit.name, user=self.user,
                criteria=crit, obj_id=self.ratedobject.pk))
        return forms

    def form_action(self):
        ct_id = self._get_ct().pk
        obj_id = self.ratedobject.pk
        return reverse('ratings:rate', kwargs={'ct_id': ct_id, 'obj_id': obj_id})

    def _get_crits(self):
        ct = self._get_ct()
        return Criteria.public.filter(content_type=ct)

    def scores_by_crit(self):
        crits = self._get_crits()
        result = []
        for crit in crits:
            scores = [sc.value for sc in Score.objects.filter(criteria=crit,
                object_id=self.ratedobject.pk)]
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
        scores = Score.objects.filter(object_id=self.ratedobject.pk)
        users = {}
        for score in scores:
            username = score.user.username
            by_crit = {
                    'name': score.criteria.name,
                    'value': score.value,
                    'comment': score.comment
                    }
            if username not in users:
                users[username] = {
                        'pub_date': score.pub_date,
                        'by_crit' : [by_crit]
                        }
            else:
                users[username]['by_crit'].append(by_crit)

        for k, v in users.items():
            numbers = [crit['value'] for crit in v['by_crit']]
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
        return result


@register.assignment_tag
def get_list_rating_for(ratedobject):
    if isinstance(ratedobject, basestring):
        raise template.TemplateSyntaxError(
                'The argument should be an object, not a string')
    return ListRating(ratedobject)


@register.assignment_tag(takes_context=True)
def get_detail_rating_for(context, ratedobject):
    if isinstance(ratedobject, basestring):
        raise template.TemplateSyntaxError(
                'The argument should be an object, not a string')
    return DetailRating(ratedobject, context['user']) # user is for rating form

