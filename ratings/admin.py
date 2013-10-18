from django.contrib import admin
from django.contrib.contenttypes import generic
from ratings.models import Criteria, Choice, Score


class ScoreInline(generic.GenericTabularInline):
    model = Score


class RatedObjectAdmin(admin.ModelAdmin):
    fields = ('avg_score', 'content_type', 'object_id')
    readonly_fields = ('avg_score', 'std_dev')


admin.site.register(Criteria)
admin.site.register(Choice)
admin.site.register(Score)

