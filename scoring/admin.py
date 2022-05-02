from django.contrib import admin
from scoring.models import ScoreType, Score, Comment, Condition, Criteria

# Register your models here.

admin.site.register(Score)
admin.site.register(ScoreType)
admin.site.register(Comment)
admin.site.register(Condition)
admin.site.register(Criteria)