import os
from gettext import ngettext

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from import_export.admin import ExportActionMixin

from .models import *


class EdgeAdmin(admin.ModelAdmin):
    model = Edge
    list_display = ['id', 'text', 'head_name', 'tail_name']

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
    list_display = ['player', 'state', 'start_time', 'end_time', 'entered_by_edge', 'reverse_enter', 'delta_time']
    list_filter = ['start_time', 'end_time', 'state__fsm', 'player', 'state', 'entered_by_edge']

    def delta_time(self, obj):
        if (obj.end_time and obj.start_time):
            return obj.end_time - obj.start_time
        return "-"


class DescriptionAdmin(admin.ModelAdmin):
    model = Description
    list_display = ['paper', 'text']

    def paper(self, obj):
        return obj.paper.id

    def text(self, obj):
        name = str(obj.text)[0:100]
        return name


class WidgetAdmin(admin.ModelAdmin):
    model = Widget
    list_display = ['id', 'widget_type', 'paper', 'name']


class RegistrationFormAdmin(admin.ModelAdmin):

    def get_registration_status_for_users(self, request, queryset):
        if len(queryset) > 0:
            selected = queryset.values_list('pk', flat=True)[0]
            return HttpResponseRedirect(f'/api/admin/export_registration_data/?q={selected}')

    model = RegistrationForm
    list_display = ['id', 'accepting_status', 'min_grade', 'max_grade', 'deadline']
    actions = [get_registration_status_for_users]


def delete_registration_receipts(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class RegistrationReceiptsAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'answer_sheet_of', 'status', 'is_participating', 'team']
    actions = [delete_registration_receipts]

    def name(self, obj):
        return obj.user.full_name


class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['user', 'receipt', 'fsm', 'current_state', 'last_visit']
    list_filter = ['last_visit', 'fsm', 'current_state']


class FSMAdmin(admin.ModelAdmin):
    model = FSM
    list_display = ['name', 'first_state', 'is_active', 'mentors']

    def mentors(self, obj):
        return ','.join(m.full_name for m in obj.mentors.all())


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['id', 'name', 'team_head', 'members']

    def members(self, obj):
        return ','.join(member.user.full_name for member in obj.members.all())


admin.site.register(Paper)
admin.site.register(RegistrationForm, RegistrationFormAdmin)
admin.site.register(Problem)
admin.site.register(AnswerSheet)
admin.site.register(RegistrationReceipt, RegistrationReceiptsAdmin)
admin.site.register(ChoiceSelection)
admin.site.register(StateAnswerSheet)
admin.site.register(Team, TeamAdmin)
admin.site.register(Invitation)

admin.site.register(FSM, FSMAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(State)
admin.site.register(Hint)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Player, PlayerAdmin)
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
admin.site.register(PlayerHistory, PlayerHistoryAdmin)
