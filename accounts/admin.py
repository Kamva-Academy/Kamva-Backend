from django.contrib import admin
from django.contrib import admin
from .models import Member, Participant, Team
class CustomUserAdmin(admin.ModelAdmin):
    model = Member

admin.site.register(Member, CustomUserAdmin)
admin.site.register(Participant)
admin.site.register(Team)

# Register your models here.
