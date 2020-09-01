from django.contrib import admin
from .models import *


class EdgeAdmin(admin.ModelAdmin):
    model = FSMEdge
    list_display = ['text', 'priority', 'head_name', 'tail_name']

    def head_name(self, obj):
        name = obj.head.name
        return name

    def tail_name(self, obj):
        name = obj.tail.name
        return name

    head_name.short_description = "سر یال"
    tail_name.short_description = "ته یال "



admin.site.register(FSM)
admin.site.register(FSMPage)
admin.site.register(FSMEdge, EdgeAdmin)
admin.site.register(Ability)
admin.site.register(FSMState)
admin.site.register(Widget)
admin.site.register(Game)
admin.site.register(ProblemSmallAnswer)
admin.site.register(SmallAnswer)
admin.site.register(TeamHistory)
