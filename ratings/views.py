from django.http import HttpResponse
from django.shortcuts import render, Http404, get_object_or_404
from ratings.models import TestDummy1

def index(request):
    """A simple list view to test ratings"""
    objlist = TestDummy1.objects.all()
    return render(request, 'ratings/index.html', {'objlist': objlist})


