from django.conf.urls import patterns, url

urlpatterns = patterns('ratings.views',
    url(r'^$', 'index'),
    url(r'^(?P<td1slug>[a-z0-9-]+)/$', 'td1_detail'),
    url(r'^(?P<td1slug>[a-z0-9-]+)/rate/$', 'td1_rate'),
)
