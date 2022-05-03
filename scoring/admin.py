from django.contrib import admin
from scoring.models import ScoreType, Score, Comment, Condition, Criteria


@admin.register(Score)
class ScoreCustomAdmin(admin.ModelAdmin):
    list_display = ['value', 'score_type', 'submitted_by']
    list_filter = ['score_type', 'answer__submitted_by']

    def submitted_by(self, obj):
        obj.answer.submitted_by


admin.site.register(ScoreType)
admin.site.register(Comment)
admin.site.register(Condition)
admin.site.register(Criteria)
