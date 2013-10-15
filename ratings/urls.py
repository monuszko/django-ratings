from django.conf.urls import patterns, url

urlpatterns = patterns('ratings.views',
    url(r'^rate/(?P<ct_id>\d+)/(?P<obj_id>\d)/$', 'rate', name='rate'),
)
