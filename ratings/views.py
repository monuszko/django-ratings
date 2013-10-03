from random import randrange
from django.http import HttpResponse
from django.shortcuts import render, Http404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models  import ContentType
from ratings.models import TestDummy1, Criteria, Score

def index(request):
    """A simple list view to test ratings"""
    objlist = TestDummy1.objects.all()
    return render(request, 'ratings/index.html', {'objlist': objlist})

def td1_detail(request, td1slug):
    """A simple detail view"""
    obj = TestDummy1.objects.get(slug=td1slug)
    return render(request, 'ratings/td1_detail.html', {'obj': obj})

@login_required
def td1_rate(request, td1slug):
    """A view to test rating"""
    obj = TestDummy1.objects.get(slug=td1slug)
    ct = ContentType.objects.get_for_model(obj)


    crits = Criteria.objects.filter(content_type=ct)
    scores = []
    for cr in crits:
        mini = cr.range_min
        maxi = cr.range_max
        value = randrange(mini, maxi+1)
        msg = u"Score for criteria {0}, range {1}-{2}".format(cr.name, mini, maxi)
        sc = Score(criteria=cr, value=value)
        scores.append(sc)
    # TODO: The form !!!
    return render(request, 'ratings/td1_rate.html', {'obj': obj,
        'scores': scores, 'crits': crits})
