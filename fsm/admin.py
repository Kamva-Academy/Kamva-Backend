import os

from django.contrib import admin
from import_export.admin import ExportActionMixin

from .models import *


class EdgeAdmin(admin.ModelAdmin):
    model = FSMEdge
    list_display = ['text', 'priority', 'head_name', 'tail_name', 'is_back_enabled']

    def head_name(self, obj):
        name = obj.head.name
        return name

    def tail_name(self, obj):
        name = obj.tail.name
        return name

    head_name.short_description = "به "
    tail_name.short_description = "از "


class AnswerAdmin(admin.ModelAdmin):
    model = UploadFileAnswer
    list_display = ['id', 'answer_file', ]

    # def name(self, obj):
    #     name = obj.problem.name
    #     return name


class SubmittedAnswerAdmin(admin.ModelAdmin):
    model = UploadFileAnswer
    list_display = ['name', 'answer_file', 'team_name']

    def name(self, obj):
        name = obj.problem.name
        return name

    def answer_file(self, obj):
        ans_file = obj.answer.uploadfileanswer.answer_file

    def team_name(self, obj):
        return str(obj.player.team.group_name)


class PlayerWorkshopAdmin(admin.ModelAdmin):
    model = PlayerWorkshop
    list_display = ['player', 'workshop', 'current_state', 'last_visit']
    list_filter = ['last_visit', 'workshop', 'current_state']

    # def name(self, obj):
    #     name = obj.problem.name
    #     return name
    #
    # def answer_file(self, obj):
    #     ans_file = obj.answer.uploadfileanswer.answer_file
    #
    #
    # def team_name(self, obj):
    #     return str(obj.player.team.group_name)


class PlayerHistoryAdmin(ExportActionMixin, admin.ModelAdmin):
    model = PlayerHistory
    list_display = ['player_workshop', 'state', 'start_time', 'end_time', 'inward_edge', 'delta_time']
    list_filter = ['start_time', 'end_time', 'state__fsm', 'player_workshop__player', 'state', 'inward_edge']

    def delta_time(self, obj):
        if (obj.end_time and obj.start_time):
            return obj.end_time - obj.start_time
        return "-"


class DescriptionAdmin(admin.ModelAdmin):
    model = Description
    list_display = ['paper', 'text_part']

    #
    def paper(self, obj):
        return obj.paper.id

    def text_part(self, obj):
        name = str(obj.text)[0:100]
        return name


def delete_registration_receipts(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class RegistrationReceiptsAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer_sheet_of']
    actions = [delete_registration_receipts]


admin.site.register(Paper)
admin.site.register(RegistrationForm)
admin.site.register(Problem)
admin.site.register(AnswerSheet)
admin.site.register(RegistrationReceipt, RegistrationReceiptsAdmin)

admin.site.register(FSM)
admin.site.register(FSMEdge, EdgeAdmin)
admin.site.register(Ability)
admin.site.register(FSMState)
admin.site.register(MainState)
admin.site.register(HelpState)
admin.site.register(Widget)
admin.site.register(Game)
admin.site.register(SmallAnswerProblem)
admin.site.register(SmallAnswer)
admin.site.register(BigAnswerProblem)
admin.site.register(BigAnswer)
admin.site.register(MultiChoiceProblem)
admin.site.register(MultiChoiceAnswer)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(Description, DescriptionAdmin)
admin.site.register(Event)
admin.site.register(UploadFileAnswer, AnswerAdmin)
admin.site.register(UploadFileProblem)
admin.site.register(SubmittedAnswer, SubmittedAnswerAdmin)

admin.site.register(PlayerHistory, PlayerHistoryAdmin)
admin.site.register(PlayerWorkshop, PlayerWorkshopAdmin)
