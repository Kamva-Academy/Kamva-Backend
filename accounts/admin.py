from django.contrib import admin
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
import sys

from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Member, Participant, Team

from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export import resources
import csv
from django.http import HttpResponse


class ParticipantResource(resources.ModelResource):
    name = Field()
    email = Field()
    email_verified = Field()

    class Meta:
        model = Participant
        fields = ['gender', 'grade', 'city', 'school', 'phone_number', 'document', 'phone_number', 'team',
                  'phone_number', 'ent_answer', 'is_activated', 'accepted']

    def dehydrate_name(self, participant):
        try:
            return participant.member.first_name
        except Exception:
            return ''

    def dehydrate_email(self, participant):
        try:
            return participant.member.email
        except Exception:
            return ''

    def dehydrate_email_verified(self, participant):
        try:
            return participant.member.is_active
        except Exception:
            return False

    def dehydrate_ent_answer(self, participant):
        try:
            if participant.ent_answer:
                return "rastaiha.ir/api/media/" + str(participant.ent_answer)
            else:
                return ''
        except Exception:
            return ''

    def dehydrate_document(self, participant):
        try:
            return "rastaiha.ir/api/media/" + str(participant.document)
        except Exception:
            return ''

    def dehydrate_team(self, participant):
        try:
            if participant.team:
                team = participant.team
                team_name = str(team.id) + " ("
                for p in team.participant_set.all():
                    team_name += str(p.member.first_name) + ", "
                team_name += ")"
                return team_name
            else:
                return ''

        except Exception:
            return ''

    def dehydrate_member(self, participant):
        try:
            return participant.member.email
        except Exception:
            return ''

    dehydrate_member.short_description = 'email'


class IsPaidFilter(admin.SimpleListFilter):
    title = 'is_paid'
    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(is_activated=True)
        elif value == 'No':
            return queryset.exclude(is_activated=True)
        return queryset


class IsEmailVerifiedFilter(admin.SimpleListFilter):
    title = 'is_email_verify'
    parameter_name = 'is_email_verify'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(is_email_verify=True)
        elif value == 'No':
            return queryset.exclude(is_email_verify=True)
        return queryset


class IsAcceptedFilter(admin.SimpleListFilter):
    title = 'is_accepted'
    parameter_name = 'is_accepted'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(accepted=True)
        elif value == 'No':
            return queryset.exclude(accepted=True)
        return queryset


class CustomUserAdmin(admin.ModelAdmin):
    model = Member
    readonly_fields = ['password', 'first_name', 'email', 'username']
    list_display = ['email', 'first_name', 'is_active']


class ParticipantInline(ExportActionMixin, admin.ModelAdmin):
    resource_class = ParticipantResource
    readonly_fields = ['document', 'gender', 'grade']
    list_display = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name','get_team', 'is_accepted', 'is_paid', 'is_email_verify']
    # fields = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name','get_team', 'is_accepted', 'is_paid', 'is_email_verify']
    list_filter = ("gender", IsEmailVerifiedFilter, IsAcceptedFilter, IsPaidFilter)
    # inlines = [CustomUserAdmin]

    def get_name(self, obj):
        try:
            return obj.member.first_name
        except:
            return False

    def is_email_verify(self, obj):
        try:
            return obj.member.is_active
        except:
            return False

    def is_paid(self, obj):
        try:
            return obj.is_activated
        except:
            return False

    def is_accepted(self, obj):
        try:
            return obj.accepted
        except:
            return False

    def get_team(self, obj):
        try:
            return obj.team
        except:
            return False


    get_name.short_description = 'name'
    is_email_verify.short_description = 'تایید ایمیل'
    is_paid.short_description = 'تایید پرداخت'
    is_accepted.short_description = 'accepted'
    get_team.short_description = 'team'
    is_accepted.boolean = True
    is_email_verify.boolean = True
    is_paid.boolean = True
    list_per_page = sys.maxsize


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['get_group_name','active', 'group_members_display',]


    def get_group_name(self, obj):
        name = str(obj.id) + "  " + str(obj.group_name)
        return name

    def group_members_display(self, obj):
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(Participant._meta.app_label, Participant._meta.model_name),
                        args=(member.pk,)),
                member.member.email)
            for member in obj.participant_set.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"
    # # inlines = [
    # #     ParticipantInline,
    # # ]
    group_members_display.short_description = "اعضای تیم"
    get_group_name.short_description = "تیم "



# Register your models here.
admin.site.register(Member, CustomUserAdmin)
admin.site.register(Participant, ParticipantInline)
admin.site.register(Team, TeamAdmin)
