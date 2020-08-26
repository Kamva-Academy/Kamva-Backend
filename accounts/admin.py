from django.contrib import admin
from django.contrib import admin
from .models import Member, Participant, Team

class CustomUserAdmin(admin.ModelAdmin):
    model = Member
    readonly_fields = ['password', 'first_name', 'email', 'username']
    list_display = ['email', 'first_name', 'is_active']



class ParticipantInline(admin.ModelAdmin):
    readonly_fields = ['document', 'gender', 'grade']
    model = Participant
    list_display = ['member','document','gender', 'grade', 'ent_answer', 'school', 'city']
    # inlines = [ParticipantPropertyItemInline]

# class TeamAdmin(admin.ModelAdmin):


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
