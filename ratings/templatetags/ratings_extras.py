from django import template
from django.contrib.auth.models import User
from django.contrib.contenttypes.models  import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from ratings.models import Score
from ratings.forms import ScoreForm

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_rating_forms(context, ratedobject):
    user = context['user']
    ct = ContentType.objects.get_for_model(ratedobject)
    crits = ct.criteria_set.all()
    forms = []
    for crit in crits:
        forms.append(ScoreForm(prefix=crit.name, user=user, criteria=crit,
            obj_id=ratedobject.pk))
    for f in forms:
        print(f.fields['value'])
    return forms

@register.simple_tag
def rate_url(ratedobject):
    ct_id = ContentType.objects.get_for_model(ratedobject).pk
    obj_id = ratedobject.pk
    return reverse('ratings:rate', kwargs={'ct_id': ct_id, 'obj_id': obj_id})

@register.simple_tag
def voters(ratedobject):
    if isinstance(ratedobject, basestring):
        raise template.TemplateSyntaxError(
                'The argument should be a model object, not string')
    ct = ContentType.objects.get_for_model(ratedobject)
    scores = Score.objects.filter(content_type=ct, object_id=ratedobject.pk)
    return len({score.user for score in scores})

