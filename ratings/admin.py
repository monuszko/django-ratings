from django.contrib import admin
from django.contrib.contenttypes import generic
from ratings.models import Criteria, Score, Opinion, RatedObject, TestDummy1

class ScoreInline(generic.GenericTabularInline):
    model = Score

class OpinionInline(generic.GenericTabularInline):
    model = Opinion

class RatedObjectInline(generic.GenericTabularInline):
    model = RatedObject

class TestDummy1Admin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'pub_date', 'content')
    inlines = [ScoreInline, OpinionInline, RatedObjectInline]


class RatedObjectAdmin(admin.ModelAdmin):
    fields = ('avg_score', 'content_type', 'object_id')
    readonly_fields = ('avg_score',)

admin.site.register(Criteria)
admin.site.register(Score)
admin.site.register(TestDummy1, TestDummy1Admin)
admin.site.register(RatedObject, RatedObjectAdmin)

