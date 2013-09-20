from django.contrib import admin
from django.contrib.contenttypes import generic
from ratings.models import Rating, Criteria, Score, TestDummy1


class RatingInLine(generic.GenericTabularInline):
    model = Rating


class TestDummy1Admin(admin.ModelAdmin):
    inlines = [
            RatingInLine,
            ]


admin.site.register(Rating)
admin.site.register(Criteria)
admin.site.register(Score)
admin.site.register(TestDummy1, TestDummy1Admin)
