from django.contrib import admin
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
import sys
import json
import os

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings

from .models import Member, Participant, Team, Payment, Mentor

from import_export.admin import ExportActionMixin
from import_export.fields import Field
from import_export import resources
from django.urls import path, reverse
from fsm.views.functions import team_change_current_state

from datetime import datetime

import logging
logger = logging.getLogger(__name__)

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
    title = 'is_email_verified'
    parameter_name = 'is_email_verify'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(member__is_active=True)
        elif value == 'No':
            return queryset.exclude(member__is_active=True)
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


class CustomUserAdmin(admin.ModelAdmin,):
    model = Member
    # readonly_fields = [ 'first_name']
    list_display = ['email', 'first_name', 'is_active']


class ParticipantInline(ExportActionMixin, admin.ModelAdmin, ):
    resource_class = ParticipantResource
    readonly_fields = ['document', 'gender', 'grade']
    list_display = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name','get_team','account_actions', 'is_accepted', 'is_paid', 'is_email_verified']
    # fields = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name','get_team', 'is_accepted', 'is_paid', 'is_email_verified']
    list_filter = ("gender", IsEmailVerifiedFilter, IsAcceptedFilter, IsPaidFilter)
    # inlines = [CustomUserAdmin]

    def get_name(self, obj):
        try:
            return obj.member.first_name
        except:
            return False

    def is_email_verified(self, obj):
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
            if(obj.team):
                display_text = str(obj.team.id) + obj.team.group_name + " (" + ", ".join([
                    "<a href={}>{}</a>".format(
                        reverse('admin:{}_{}_change'.format(Participant._meta.app_label, Participant._meta.model_name),
                                args=(member.pk,)),
                        member.member.email)
                    for member in obj.team.participant_set.all()
                ]) + ")"
                if display_text:
                    return mark_safe(display_text)
                return "-"
        except:
            return ''



    def account_actions(self, obj):
        try:
            if obj.accepted:
                return mark_safe('<a class="button" href="' + reverse('admin:unaccept_member',
                                                                      args=[obj.pk]) + '">رد کن</a>' + '&nbsp;')

            else:
                return mark_safe('<a class="button" href="' + reverse('admin:accept_member',
                                                                      args=[obj.pk]) + '">قبول کن</a>' + '&nbsp;')
        except:
            return None

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'accept/<int:pk>/',
                self.accept_member,
                name='accept_member',
            ),
            path(
                'unaccept/<int:pk>/',
                self.unaccept_member,
                name='unaccept_member',
            )
        ]
        return custom_urls + urls

    def accept_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.accepted = True
        participant.save()
        return redirect('/api/admin/accounts/participant')

    def unaccept_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.accepted = False
        participant.save()
        return redirect('/api/admin/accounts/participant')

    get_name.short_description = 'name'
    is_email_verified.short_description = 'تایید ایمیل'
    is_paid.short_description = 'تایید پرداخت'
    is_accepted.short_description = 'accepted'
    get_team.short_description = 'team'
    is_accepted.boolean = True
    is_email_verified.boolean = True
    is_paid.boolean = True
    account_actions.short_description = 'ACCEPT'


    list_per_page = sys.maxsize


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['get_group_name', 'active', 'group_members_display', 'team_members_count', 'team_status', 'current_state']

    change_list_template = 'admin/accounts/change_list_team.html'

    class Media:
        js = (
            'scripts/admin-confirm.js',
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'unset_all_current_states/',
                self.unset_all_current_states,
                name='unset_all_current_states',
            ),
        ]
        return custom_urls + urls

    def unset_all_current_states(self, request, *args, **kwargs):
        qs = Team.objects.all()
        ll = list(qs.values_list('id', 'current_state'))
        json.dump(ll, open(os.path.join(settings.MEDIA_ROOT,
                           'current_states_before_clear_%s.json' % datetime.now().isoformat()), 'w'))
        qs.update(current_state=None)
        return HttpResponse('Unseting current_states for %s teams was successfull!' % qs.count())

    def save_model(self, request, obj, form, change):
        if change:
            logger.debug(f'changed state team {obj.id}')
            team_change_current_state(obj, obj.current_state)
        super().save_model(request, obj, form, change)

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

    def team_members_count(self, obj):
        return obj.participant_set.all().count()
    
    def team_status(self, obj):
        accept_count = 0
        for p in obj.participant_set.all():
            if p.accepted:
                accept_count += 1  
        if accept_count == 0: return False
        elif accept_count == obj.participant_set.all().count(): return True
        else: return None
    # # inlines = [
    # #     ParticipantInline,
    # # ]
    group_members_display.short_description = "اعضای تیم"
    get_group_name.short_description = "تیم "
    team_members_count.short_description = "تعداد اعضا"
    team_status.short_description = "وضعیت قبولی تیم"
    team_status.boolean = True


class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ['get_user_name', 'uniq_code', 'status', 'amount' , 'get_team' ]

    def get_user_name(self, obj):
        name = str(obj.user.member.first_name) + "(" + str(obj.user.member.username) + ")"
        return name

    def get_team(self, obj):
        name = str(obj.user.team)
        return name


    get_user_name.short_description = "نام"
    get_team.short_description = "تیم"


# Register your models here.
admin.site.register(Member, CustomUserAdmin)
admin.site.register(Participant, ParticipantInline)
admin.site.register(Team, TeamAdmin)
admin.site.register(Mentor)
admin.site.register(Payment, PaymentAdmin)
