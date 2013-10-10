from django.conf.urls import patterns, url

urlpatterns = patterns('ratings.views',
    url(r'^$', 'index', name='index'),
    url(r'^rate/(?P<ct_id>\d+)-(?P<obj_id>\d+)/$', 'rate', name='rate'),
    url(r'^(?P<td1slug>[a-z0-9-]+)/$', 'td1_detail', name='td1_detail'),
)
