from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, Http404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

from ratings.models import Criteria, Score, ScoreForm
from django.core.exceptions import ValidationError

@login_required
def rate(request, ct_id, obj_id):
    ct = ContentType.objects.get_for_id(ct_id)
    crits = {crit.name: crit for crit in ct.criteria_set.all()}
    if request.method == "POST":
        sforms = []
        for critname in crits:
            sforms.append(ScoreForm(
                request.POST,
                prefix = critname,
                user = request.user,
                criteria = crits[critname],
                obj_id = obj_id)
                )
        if all([sf.is_valid() for sf in sforms]):
            for sf in sforms:
                # TODO: check for malicious POST ?
                score = sf.save(commit=False)
                score.content_type = sf.criteria.content_type
                score.object_id = sf.obj_id
                score.user = sf.user
                score.criteria = sf.criteria
                score.save()
            obj = ct.get_object_for_this_type(pk=obj_id)
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            pass # Should I put something here ?
    return render_to_response('ratings/rate.html', {'score_forms': sforms},
            context_instance=RequestContext(request))

