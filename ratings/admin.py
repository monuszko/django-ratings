from django.contrib import admin
from django.contrib.contenttypes import generic
from ratings.models import Criteria, Choice, Score


class ScoreInline(generic.GenericTabularInline):
    model = Score


class RatedObjectAdmin(admin.ModelAdmin):
    fields = ('avg_score', 'content_type', 'object_id')
    readonly_fields = ('avg_score', 'std_dev')


class CriteriaAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = self.model.objects.get_query_set()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Choice)
admin.site.register(Score)

