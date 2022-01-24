import os
import csv
from gettext import ngettext

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from import_export.admin import ExportActionMixin

from fsm.models import Edge, Paper, RegistrationForm, Problem, AnswerSheet, RegistrationReceipt, ChoiceSelection, Team, \
    Invitation, CertificateTemplate, Font, FSM, State, Hint, Widget, Video, Image, Player, Game, SmallAnswerProblem, \
    SmallAnswer, BigAnswerProblem, BigAnswer, MultiChoiceProblem, MultiChoiceAnswer, Choice, Answer, Description, Event, \
    UploadFileAnswer, UploadFileProblem, PlayerHistory, timedelta, timezone, Article


class EdgeAdmin(admin.ModelAdmin):
    model = Edge
    list_display = ['id', 'text', 'head_name', 'tail_name', 'is_visible']

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
    search_fields = ['answer_file']
    list_filter = ['problem', 'is_final_answer']

    # def name(self, obj):
    #     name = obj.problem.name
    #     return name


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


class PaperAdmin(admin.ModelAdmin):
    model = Paper
    list_display = ['id', 'since', 'till', 'is_exam']


class RegistrationFormAdmin(admin.ModelAdmin):

    def get_registration_status_for_users(self, request, queryset):
        if len(queryset) > 0:
            selected = queryset.values_list('pk', flat=True)[0]
            return HttpResponseRedirect(f'/api/admin/export_registration_data/?q={selected}')

    model = RegistrationForm
    list_display = ['id', 'accepting_status', 'min_grade', 'max_grade', 'since', 'till']
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
    list_display = ['name', 'first_state', 'is_active', 'mentors_num', 'mentors_list', 'online_teams_in_last_hour']

    def mentors_list(self, obj):
        return ','.join(m.full_name for m in obj.mentors.all())

    def mentors_num(self, obj):
        return len(obj.mentors.all())

    def online_teams_in_last_hour(self, obj):
        return round(len(obj.players.filter(
            last_visit__gt=timezone.now() - timedelta(hours=1))) / obj.team_size if obj.team_size > 0 else 1)


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['id', 'name', 'team_head', 'members', 'has_been_online_in_last_hour']

    def members(self, obj):
        return ','.join(member.user.full_name for member in obj.members.all())

    def has_been_online_in_last_hour(self, obj):
        for m in obj.members.all():
            if m.players.filter(last_visit__gt=timezone.now() - timedelta(hours=1)).first():
                return True
        return False


class StateAdmin(admin.ModelAdmin):
    model = State
    list_display = ['id', 'name', 'fsm']


class SmallAnswerProblemAdmin(admin.ModelAdmin):

    def solution_csv(self, request, queryset):

        file = open('small-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = SmallAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow([i.problem.name, i.problem.text, i.text, i.submitted_by])

            else:
                writer.writerow([i.problem.name, None, i.text, i.submitted_by])

            ctr += 1

        file.close()

        f = open('small-answers.csv', 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=small-answers.csv'
        return response

    actions = [solution_csv]


class BigAnswerProblemAdmin(admin.ModelAdmin):

    def solution_csv(self, request, queryset):

        file = open('big-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = BigAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow([i.problem.name, i.problem.text, i.text, i.submitted_by])

            else:
                writer.writerow([i.problem.name, None, i.text, i.submitted_by])

            ctr += 1

        file.close()

        f = open('big-answers.csv', 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=big-answers.csv'
        return response

    actions = [solution_csv]


admin.site.register(Paper, PaperAdmin)
admin.site.register(RegistrationForm, RegistrationFormAdmin)
admin.site.register(Problem)
admin.site.register(AnswerSheet)
admin.site.register(RegistrationReceipt, RegistrationReceiptsAdmin)
admin.site.register(ChoiceSelection)
admin.site.register(Team, TeamAdmin)
admin.site.register(Invitation)
admin.site.register(CertificateTemplate)
admin.site.register(Font)

admin.site.register(FSM, FSMAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Hint)
admin.site.register(Article)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(Video)
admin.site.register(Image)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Game)
admin.site.register(SmallAnswerProblem, SmallAnswerProblemAdmin)
admin.site.register(SmallAnswer)
admin.site.register(BigAnswerProblem, BigAnswerProblemAdmin)
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
