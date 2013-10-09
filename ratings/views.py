from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, Http404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

from ratings.models import TestDummy1, Criteria, Score
from ratings.forms import ScoreForm
from django.core.exceptions import ValidationError

def index(request):
    """A simple list view to test ratings"""
    objlist = TestDummy1.objects.all()
    return render(request, 'ratings/index.html', {'objlist': objlist})


def td1_detail(request, td1slug):
    """A simple detail view"""
    obj = TestDummy1.objects.get(slug=td1slug)
    return render(request, 'ratings/td1_detail.html', {'obj': obj})

# TODO: object-agnostic Rate view
@login_required
def td1_rate(request, td1slug):
    obj = TestDummy1.objects.get(slug=td1slug)
    ct = ContentType.objects.get_for_model(obj)
    crits = Criteria.objects.filter(content_type=ct)
    if request.method == "POST":
        sforms = []
        for crit in crits:
            sforms.append(ScoreForm(request.POST, prefix=crit.name))
        sforms = [ScoreForm(request.POST, prefix=crit.name) for crit in crits]
        if all([sf.is_valid() for sf in sforms]):
            for sf in sforms:
                # Manual protection against malicious POST attacks :(
                # I think "user" field is the only one that REALLY needs to be
                # protected, because unique_together takes care of multi-votes.
                # Rating ContenTypes like 'permission' would be silly.
                if sf['user'].value() != unicode(request.user.pk):
                    raise ValidationError
                elif sf['content_type'].value() != unicode(ct.pk):
                    raise ValidationError
                sf.save()
            # TODO: redirect
            return HttpResponseRedirect('/ratings/')
    else:
        sforms = [] 
        for crit in crits:
            sc = Score(user=request.user, content_type=ct, object_id=obj.pk,
                       criteria=crit)
            sforms.append(ScoreForm(prefix=crit.name, instance=sc))
    return render_to_response('ratings/td1_rate.html', {'score_forms': sforms},
            context_instance=RequestContext(request))

