from django.contrib import admin
from event_metadata.models import StaffInfo, StaffTeam

class StaffInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'registration_form', 'title']
    list_filter = ['registration_form']
    search_fields = ['user__first_name', 'user__last_name', 'title']


admin.site.register(StaffInfo, StaffInfoAdmin)
admin.site.register(StaffTeam)