from django.contrib import admin

from question.models import InviteeUsernameQuestion, InviteeUsernameResponse

@admin.register(InviteeUsernameQuestion)
class InviteeUsernameQuestionAdmin(admin.ModelAdmin):
    pass

@admin.register(InviteeUsernameResponse)
class InviteeUsernameResponseAdmin(admin.ModelAdmin):
    pass
