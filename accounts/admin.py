from django.contrib import admin
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin

from .models import Member, Participant, Team

from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export import resources
import csv
from django.http import HttpResponse


class ParticioantResource(resources.ModelResource):
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
            return participant.member.is_activated
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




class CustomUserAdmin(admin.ModelAdmin):
    model = Member
    readonly_fields = ['password', 'first_name', 'email', 'username']
    list_display = ['email', 'first_name', 'is_active']


class ParticipantInline(ExportActionMixin, admin.ModelAdmin):
    resource_class = ParticioantResource
    readonly_fields = ['document', 'gender', 'grade']
    list_display = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name', 'is_accepted', 'is_doc_verify', 'is_email_verify']
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

    def is_doc_verify(self, obj):
        try:
            return obj.is_activated
        except:
            return False

    def is_accepted(self, obj):
        try:
            return obj.accepted
        except:
            return False


    get_name.short_description = 'name'
    is_doc_verify.short_description = 'تایید مدارک'
    is_email_verify.short_description = 'تایید ایمیل'
    is_accepted.short_description = 'accepted'
    is_accepted.boolean = True
    is_email_verify.boolean = True
    is_doc_verify.boolean = True

    # inlines = [ParticipantPropertyItemInline]


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['active']
    # inlines = [
    #     ParticipantInline,
    # ]


# Register your models here.
admin.site.register(Member, CustomUserAdmin)
admin.site.register(Participant, ParticipantInline)
admin.site.register(Team,)
