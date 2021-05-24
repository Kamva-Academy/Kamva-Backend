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

from .models import Member, Participant, Team, Payment, Mentor, Player, DiscountCode, User

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


zero_media_root = "zero.rastaiha.ir/api/media/"

class ParticipantResource(resources.ModelResource):
    name = Field()
    email = Field()
    phone = Field()
    username = Field()
    answer = Field()
    doc = Field()
    gender = Field()
    school = Field()
    city = Field()
    team_count = Field()
    team = Field()


    class Meta:
        model = Participant
        fields = ['gender', 'grade', 'city', 'school', 'phone_number', 'document', 'phone_number', 'team',
                  'phone_number', 'ent_answer', 'is_activated', 'team_count']

    def dehydrate_name(self, participant):
        try:
            return participant.member.first_name
        except Exception:
            return ''

    def dehydrate_username(self, participant):
        try:
            return participant.member.username
        except Exception:
            return ''

    def dehydrate_team(self, participant):
        try:
            return participant.event_team
        except Exception:
            return ''

    def dehydrate_team_count(self, participant):
        print("helooooo")
        try:
            t = participant.event_team
            return len(participant.event_team.team_participants.all())
        except Exception:
            return ''

    def dehydrate_email(self, participant):
        try:
            return participant.member.email
        except Exception:
            return ''

    def dehydrate_gender(self, participant):
        try:
            return participant.member.gender
        except Exception:
            return ''

    def dehydrate_grade(self, participant):
        try:
            return participant.member.grade
        except Exception:
            return ''

    def dehydrate_school(self, participant):
        try:
            return participant.member.school
        except Exception:
            return ''

    def dehydrate_city(self, participant):
        try:
            return participant.member.city
        except Exception:
            return ''

    def dehydrate_phone(self, participant):
        try:
            return participant.member.phone_number
        except Exception:
            return ''

    def dehydrate_answer(self, participant):
        try:
            if participant.selection_doc:
                return zero_media_root + str(participant.selection_doc)
            else:
                return ''
        except Exception:
            return ''

    def dehydrate_doc(self, participant):
        try:
            if participant.member.document:
                return zero_media_root + str(participant.member.document)
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


# class IsEmailVerifiedFilter(admin.SimpleListFilter):
#     title = 'is_email_verified'
#     parameter_name = 'is_email_verify'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('Yes', 'Yes'),
#             ('No', 'No'),
#         )
#
#     def queryset(self, request, queryset):
#         value = self.value()
#         if value == 'Yes':
#             return queryset.filter(member__is_active=True)
#         elif value == 'No':
#             return queryset.exclude(member__is_active=True)
#         return queryset


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
    list_display = ['username', 'email', 'first_name', 'is_active']


class ParticipantInline(ExportActionMixin, admin.ModelAdmin, ):
    resource_class = ParticipantResource
    # readonly_fields = ['document', 'gender', 'grade']
    # ,'document','member__gender', 'member__grade', 'member__school', 'member__city', 'get_name','get_team',
    list_display = ['member', 'get_name', 'get_team','get_grade',
                    'get_gender','get_doc','get_school', 'get_city','selection_doc', 'get_phone',
                    'par_is_paid', 'par_is_accepted','par_is_participated', 'par_accepting','par_finalize',]
    # fields = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city', 'get_name','get_team', 'is_accepted', 'is_paid', 'is_email_verified']
    # list_filter = ('IsPaidFilter')

    # inlines = [CustomUserAdmin]

    def get_name(self, obj):
        try:
            return obj.member.first_name
        except:
            return False

    def get_name(self, obj):
        try:
            return obj.member.first_name
        except:
            return False

    def get_city(self, obj):
        try:
            return obj.member.city
        except:
            return False

    def get_school(self, obj):
        try:
            return obj.member.school
        except:
            return False

    def get_doc(self, obj):
        # try:
        link = "<a href={}>{}</a>".format(
                    zero_media_root + str(obj.member.document),
        obj.member.first_name)
        return mark_safe(link)
        # except:
        #     return False

    def get_gender(self, obj):
        try:
            return obj.member.gender
        except:
            return False

    def get_phone(self, obj):
        try:
            return obj.member.phone_number
        except:
            return False

    def get_grade(self, obj):
        try:
            return obj.member.grade
        except:
            return False

    def par_is_paid(self, obj):
        try:
            return obj.is_paid
        except:
            return False

    def par_is_accepted(self, obj):
        try:
            return obj.is_accepted
        except:
            return False

    def par_is_participated(self, obj):
        try:
            return obj.is_participated
        except:
            return False

    def get_team(self, obj):
        try:
            if(obj.event_team):
                display_text = str(obj.event_team.id) + '_' + obj.event_team.group_name + " (" + ", ".join([
                    "<a href={}>{}</a>".format(
                        reverse('admin:{}_{}_change'.format(Participant._meta.app_label, Participant._meta.model_name),
                                args=(par.pk,)),
                        par.member.username)
                    for par in obj.event_team.team_participants.all()
                ]) + ")"
                if display_text:
                    return mark_safe(display_text)
            return "-"
        except:
            return ''

    def par_accepting(self, obj):
        try:
            if obj.is_accepted:
                return mark_safe('<a class="button" href="' + reverse('admin:unaccept_member',
                                                                      args=[obj.pk]) + '">رد کن</a>' + '&nbsp;')
            else:
                return mark_safe('<a class="button" href="' + reverse('admin:accept_member',
                                                                      args=[obj.pk]) + '">قبول کن</a>' + '&nbsp;')
        except:
            return None

    def par_finalize(self, obj):
        try:
            if obj.is_participated:
                return mark_safe('<a class="button" href="' + reverse('admin:unfinalize_member',
                                                                      args=[obj.pk]) + '">نهایی کن</a>' + '&nbsp;')

            else:
                return mark_safe('<a class="button" href="' + reverse('admin:finalize_member',
                                                                      args=[obj.pk]) + '">حذف کن</a>' + '&nbsp;')
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
            ),
            path(
                'unfinalize/<int:pk>/',
                self.unfinalize_member,
                name='unfinalize_member',
            ),
            path(
                'finalize/<int:pk>/',
                self.finalize_member,
                name='finalize_member',
            )
        ]
        return custom_urls + urls

    def accept_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.is_accepted = True
        participant.save()
        return redirect('/api/admin/accounts/participant')

    def unaccept_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.is_accepted = False
        participant.save()
        return redirect('/api/admin/accounts/participant')

    def finalize_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.is_participated = True
        participant.save()
        return redirect('/api/admin/accounts/participant')

    def unfinalize_member(self, request, *args, **kwargs):
        participant = Participant.objects.get(pk=kwargs['pk'])
        participant.is_participated = False
        participant.save()
        return redirect('/api/admin/accounts/participant')

    get_name.short_description = 'نام'
    par_is_accepted.boolean = True
    par_is_paid.boolean = True
    par_is_participated.boolean = True
    par_is_paid.short_description = 'تایید پرداخت'
    par_is_accepted.short_description = 'پذیرش'
    get_team.short_description = 'تیم'
    par_is_participated.short_description = 'نهایی شده؟'
    par_accepting.short_description = 'گزینش'
    par_finalize.short_description = 'نهایی کردن'
    get_doc.short_description = 'مدرک احراز هویت'
    get_city.short_description = 'شهر'
    get_school.short_description = 'مدرسه'
    get_gender.short_description = 'دختر/پسر'
    get_phone.short_description = 'شماره تماس'
    get_grade.short_description = 'پایه'


    list_per_page = sys.maxsize


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['get_group_name', 'active', 'group_members_display', 'team_members_count', 'team_status']

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
            # team_change_current_state(obj, obj.current_state)
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
            for member in obj.team_participants.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"

    def team_members_count(self, obj):
        return obj.team_participants.all().count()
    
    def team_status(self, obj):
        accept_count = 0
        for p in obj.team_participants.all():
            accept_count += 1
        if accept_count == 0: return False
        elif accept_count == obj.team_participants.all().count(): return True
        else: return None

    group_members_display.short_description = "اعضای تیم"
    get_group_name.short_description = "تیم "
    team_members_count.short_description = "تعداد اعضا"
    team_status.short_description = "وضعیت قبولی تیم"
    team_status.boolean = True


class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ['get_user_name', 'uniq_code', 'status', 'amount' , 'get_team' ]

    def get_user_name(self, obj):
        name = str(obj.participant.member.first_name) + "(" + str(obj.participant.member.username) + ")"
        return name

    def get_team(self, obj):
        name = str(obj.participant.team)
        return name


    get_user_name.short_description = "نام"
    get_team.short_description = "تیم"


# Register your models here.
admin.site.register(Member, CustomUserAdmin)
admin.site.register(User)
admin.site.register(Participant, ParticipantInline)
admin.site.register(Team, TeamAdmin)
admin.site.register(Mentor)
admin.site.register(Player)
admin.site.register(DiscountCode)
admin.site.register(Payment, PaymentAdmin)
