from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, Http404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

from ratings.models import Criteria, Score
from ratings.forms import ScoreForm
from django.core.exceptions import ValidationError

# TODO: object-agnostic Rate view
@login_required
def rate(request, ct_id, obj_id):
    ct = ContentType.objects.get_for_id(ct_id)
    obj = ct.get_object_for_this_type(pk = obj_id)

    ct = ContentType.objects.get_for_model(obj)
    crits = Criteria.objects.filter(content_type=ct)
    if request.method == "POST":
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
    return render_to_response('ratings/rate.html', {'score_forms': sforms},
            context_instance=RequestContext(request))

