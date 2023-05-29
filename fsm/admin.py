import csv

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from import_export.admin import ExportActionMixin

from fsm.models import Edge, Paper, RegistrationForm, Problem, AnswerSheet, RegistrationReceipt, ChoiceSelection, Team, \
    Invitation, CertificateTemplate, Font, FSM, State, WidgetHint, Hint, Widget, Video, Audio, Image, Player, Game, SmallAnswerProblem, \
    SmallAnswer, BigAnswerProblem, BigAnswer, MultiChoiceProblem, MultiChoiceAnswer, Choice, Answer, Description, Event, \
    UploadFileAnswer, UploadFileProblem, PlayerHistory, timedelta, timezone, Article, Tag, Aparat

from fsm.utils import get_django_file


class EdgeAdmin(admin.ModelAdmin):
    model = Edge
    list_display = ['id', 'text', 'head_name', 'tail_name', 'is_visible']
    list_filter = ['is_visible', 'head__name', 'tail__name']

    def head_name(self, obj):
        name = obj.head.name
        return name

    def tail_name(self, obj):
        name = obj.tail.name
        return name

    head_name.short_description = "به "
    tail_name.short_description = "از "


class UploadFileAnswerAdmin(admin.ModelAdmin):
    model = UploadFileAnswer
    list_display = ['id', 'problem', 'answer_file', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']


class PlayerHistoryAdmin(ExportActionMixin, admin.ModelAdmin):
    model = PlayerHistory
    list_display = ['player', 'state', 'start_time', 'end_time',
                    'entered_by_edge', 'reverse_enter', 'delta_time']
    list_filter = ['start_time', 'end_time',
                   'state__fsm', 'state', 'entered_by_edge']

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
    list_filter = ['widget_type', 'name']
    search_fields = ['name']


class PaperAdmin(admin.ModelAdmin):
    model = Paper
    list_display = ['id', 'since', 'till', 'criteria', 'is_exam']
    list_filter = ['is_exam']


class RegistrationFormAdmin(admin.ModelAdmin):

    def get_registration_status_for_users(self, request, queryset):
        if len(queryset) > 0:
            selected = queryset.values_list('pk', flat=True)[0]
            # TODO: fix bug
            return HttpResponseRedirect(f'/api/admin/export_registration_data/?q={selected}')

    model = RegistrationForm
    list_display = ['id', 'event_or_fsm', 'accepting_status',
                    'min_grade', 'max_grade', 'audience_type']
    list_display_links = ['id', 'event_or_fsm']
    actions = [get_registration_status_for_users]


def delete_registration_receipts(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


def download_csv(modeladmin, request, queryset):
    import csv
    f = open('registration_receipts.csv', 'w')
    writer = csv.writer(f)
    a_receipt = queryset[0]
    problems = []
    for widget in a_receipt.answer_sheet_of.widgets.all():
        print(widget.widget_type)
        if 'problem' in widget.widget_type.lower():
            problem = widget
            problems.append(problem.id)
    header = ['user', 'status', 'is_participating', 'team']
    writer.writerow(
        header + [f'widget {problem}' for problem in problems])
    for registration_receipt in queryset:
        row = [registration_receipt.user, registration_receipt.status,
               registration_receipt.is_participating, registration_receipt.team]
        for problem_id in problems:
            for answer in registration_receipt.answers.all():
                if answer.problem.id == problem_id:
                    row.append(answer.get_string_answer())
        writer.writerow(row)
    f.close()
    f = open('registration_receipts.csv', 'r')
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=registration_receipts.csv'
    return response


class RegistrationReceiptsAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'answer_sheet_of',
                    'status', 'is_participating', 'team']
    list_filter = ['answer_sheet_of', 'status', 'is_participating']
    actions = [delete_registration_receipts, download_csv]

    def name(self, obj):
        return obj.user.full_name


class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['user', 'receipt', 'fsm', 'current_state', 'last_visit']
    list_filter = ['last_visit', 'fsm', 'current_state']
    search_fields = ['user__username']


class FSMAdmin(admin.ModelAdmin):
    model = FSM
    list_display = ['name', 'first_state', 'is_active',
                    'mentors_num', 'mentors_list', 'online_teams_in_last_hour']
    list_filter = ['name']
    search_fields = ['name']

    def mentors_list(self, obj):
        return ','.join(m.full_name for m in obj.mentors.all())

    def mentors_num(self, obj):
        return len(obj.mentors.all())

    def online_teams_in_last_hour(self, obj):
        return round(len(obj.players.filter(
            last_visit__gt=timezone.now() - timedelta(hours=1))) / obj.team_size if obj.team_size > 0 else 1)


def download_team_info_csv(modeladmin, request, queryset):
    import csv
    f = open('teams-info.csv', 'w', encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(['team_name', 'users'])
    for team in queryset:
        members = team.members.all()
        team_info = [team.name, ]
        for member in members:
            team_info.append(
                f'{member.user.first_name} {member.user.last_name}')
        writer.writerow(team_info)

    f.close()
    f = open('teams-info.csv', 'r')
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=teams-info.csv'
    return response


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['name', 'event_or_fsm', 'team_head',
                    'members', 'has_been_online_in_last_hour']
    list_filter = ['registration_form']
    search_fields = ['name']
    actions = [download_team_info_csv]

    def event_or_fsm(self, obj):
        return obj.registration_form.event_or_fsm

    def members(self, obj):
        return ', '.join(member.user.full_name for member in obj.members.all())

    def has_been_online_in_last_hour(self, obj):
        for m in obj.members.all():
            if m.players.filter(last_visit__gt=timezone.now() - timedelta(hours=1)).first():
                return True
        return False


class StateAdmin(admin.ModelAdmin):
    model = State
    list_display = ['id', 'name', 'fsm']
    list_filter = ['name']
    search_fields = ['name']


class SmallAnswerProblemAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper', 'widget_type', 'creator']
    list_filter = ['widget_type']
    search_fields = ['name']

    def solution_csv(self, request, queryset):

        file = open('small-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = SmallAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow(
                    [i.problem.name, i.problem.text, i.text, i.submitted_by])

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
    list_display = ['name', 'paper', 'widget_type', 'creator']
    list_filter = ['widget_type']
    search_fields = ['name']

    def solution_csv(self, request, queryset):

        file = open('big-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = BigAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow(
                    [i.problem.name, i.problem.text, i.text, i.submitted_by])

            else:
                writer.writerow([i.problem.name, None, i.text, i.submitted_by])

            ctr += 1

        file.close()

        f = open('big-answers.csv', 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=big-answers.csv'
        return response

    actions = [solution_csv]


@admin.register(AnswerSheet)
class AnswerSheetCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_sheet_type']
    list_display_links = ['id', 'answer_sheet_type']
    list_filter = ['answer_sheet_type']
    search_fields = ['answer_sheet_type']


@admin.register(Problem)
class ProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type',
                    'creator', 'required']
    list_display_links = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name', 'widget_type', 'required']
    search_fields = ['name']

    def download_final_answers_scores(self, request, queryset):
        score_types = set()
        problems = {}
        for p in queryset:
            answers = []
            score_types |= set(
                st for st in p.paper.score_types.all().values_list('name', flat=True))
            for ans in p.answers.filter(is_final_answer=True):
                ans_dict = {'id': ans.id,
                            'first_name': ans.submitted_by.first_name,
                            'phone_number': ans.submitted_by.phone_number,
                            'last_name': ans.submitted_by.last_name,
                            'school': ans.submitted_by.school_studentship.school.name if ans.submitted_by.school_studentship.school else None,
                            'grade': ans.submitted_by.school_studentship.grade,
                            'province': ans.submitted_by.province,
                            'city': ans.submitted_by.city,
                            'gender': ans.submitted_by.gender,
                            'national_code': ans.submitted_by.national_code,
                            }
                for score in ans.scores.all():
                    ans_dict[score.type.name] = score.value
                answers.append(ans_dict)
            problems[p] = answers

        file = open('answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_id', 'answer_id', 'first_name', 'last_name', 'phone_number', 'school', 'grade', 'province', 'city', 'gender',
             'national_code'] + [st for st in score_types])
        for p in queryset:
            for a in problems[p]:
                writer.writerow([p.id, a['id'], a['first_name'], a['last_name'], a['phone_number'], a['school'], a['grade'], a['province'],
                                 a['city'], a['gender'], a['national_code']] + [a.get(st, '') for st in score_types])
        file.close()

        f = open('answers.csv', 'rb')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=answers.csv'
        return response

    download_final_answers_scores.short_description = 'export scored answers'
    actions = [download_final_answers_scores]


@admin.register(MultiChoiceAnswer)
class MultiChoiceAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem']
    list_display_links = ['id', 'problem']
    list_filter = ['problem']


@admin.register(ChoiceSelection)
class ChoiceSelectionCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'multi_choice_answer', 'choice']
    list_display_links = ['id', 'multi_choice_answer', 'choice']
    list_filter = ['multi_choice_answer', 'choice']


@admin.register(Invitation)
class InvitationCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'invitee', 'team', 'status']
    list_display_links = ['id', 'invitee', 'team']
    list_filter = ['status']


@admin.register(CertificateTemplate)
class CertificateTemplateCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'certificate_type', 'name_X',
                    'name_Y', 'registration_form', 'font_size']
    list_display_links = ['id', 'certificate_type']
    list_filter = ['certificate_type', 'name_X', 'name_Y']
    search_fields = ['certificate_type']


@admin.register(MultiChoiceProblem)
class MultiChoiceProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_display_links = ['id', 'name']
    list_filter = ['widget_type']
    search_fields = ['name']


@admin.register(Answer)
class AnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_type', 'answer_sheet',
                    'submitted_by', 'is_final_answer', 'is_correct', 'created_at']
    list_filter = ['answer_type', 'is_final_answer',
                   'is_correct', 'created_at']
    search_fields = ['submitted_by__username']


@admin.register(BigAnswer)
class BigAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(SmallAnswer)
class SmallAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'widget_type', 'creator']
    list_filter = ['problem__name']

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(Article)
class ArticleCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_draft', 'all_tags', 'publisher']
    list_filter = ['name']

    def all_tags(self, obj):
        return ','.join(m.name for m in obj.tags.all())


@admin.register(Game)
class GameCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name']
    search_fields = ['name']


def download_files_from_links(self, request, queryset):
    for media in queryset:
        try:
            if not media.file:
                link_file = get_django_file(media.link)
                media.file = link_file
                media.save()
        except:
            pass


@admin.register(Video)
class VideoCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name']
    search_fields = ['name']
    actions = [download_files_from_links]


@admin.register(Audio)
class AudioCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Aparat)
class AparatCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Image)
class ImageCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_filter = ['name']
    search_fields = ['name']
    actions = [download_files_from_links]


@admin.register(Hint)
class HintCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper_type', 'creator']
    list_filter = ['paper_type']


@admin.register(WidgetHint)
class WidgetHintCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper_type', 'creator']
    list_filter = ['paper_type']


@admin.register(Choice)
class ChoiceCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem', 'text']


@admin.register(Event)
class EventCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'registration_form',
                    'merchandise', 'creator', 'holder']
    list_display_links = ['id', 'name']


@admin.register(UploadFileProblem)
class UploadFileProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'paper', 'widget_type', 'creator']
    list_display_links = ['id', 'name']
    list_filter = ['widget_type']
    search_fields = ['name']


admin.site.register(Paper, PaperAdmin)
admin.site.register(RegistrationForm, RegistrationFormAdmin)
admin.site.register(RegistrationReceipt, RegistrationReceiptsAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Font)
admin.site.register(FSM, FSMAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(BigAnswerProblem, BigAnswerProblemAdmin)
admin.site.register(SmallAnswerProblem, SmallAnswerProblemAdmin)
admin.site.register(Description, DescriptionAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerHistory, PlayerHistoryAdmin)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(UploadFileAnswer, UploadFileAnswerAdmin)
admin.site.register(Tag)
# admin.site.register(Invitation)
# admin.site.register(CertificateTemplate)
# admin.site.register(ChoiceSelection)
# admin.site.register(Problem)
# admin.site.register(AnswerSheet)
# admin.site.register(MultiChoiceAnswer)
# admin.site.register(MultiChoiceProblem)
# admin.site.register(Answer)
# admin.site.register(BigAnswer)
# admin.site.register(SmallAnswer)
# admin.site.register(Article)
# admin.site.register(Game)
# admin.site.register(Video)
# admin.site.register(Image)
# admin.site.register(Hint)
# admin.site.register(Choice)
# admin.site.register(Event)
# admin.site.register(UploadFileProblem)
