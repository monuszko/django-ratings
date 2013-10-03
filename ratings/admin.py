from django.contrib import admin
from django.contrib.contenttypes import generic
from ratings.models import Criteria, Score, Opinion, TestDummy1

class ScoreInLine(generic.GenericTabularInline):
    model = Score

class OpinionInLine(generic.GenericTabularInline):
    model = Opinion

class TestDummy1Admin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('avg_score', 'std_deviation')
    fields = ('title', 'slug', 'pub_date', 'content', 'avg_score', 'std_deviation')
    inlines = [ScoreInLine, OpinionInLine]

admin.site.register(Criteria)
admin.site.register(Score)
admin.site.register(TestDummy1, TestDummy1Admin)
