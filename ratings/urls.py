from django.conf.urls import patterns, url

urlpatterns = patterns('ratings.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<td1slug>[a-z0-9-]+)/$', 'td1_detail', name='td1_detail'),
    url(r'^(?P<td1slug>[a-z0-9-]+)/rate/$', 'td1_rate', name='td1_rate'),
)
