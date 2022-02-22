from django.contrib import admin

from event_metadata.models import StaffInfo, EventImage
# Register your models here.

class StaffInfoAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'account',
        'event',
        'description',
        'role',
    ]

    list_filter = ['event', 'account']
    search_fields = ['account__first_name', 'account__last_name']

class EventImageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'event', 'image']
    
    list_filter = ['event']

admin.site.register(StaffInfo, StaffInfoAdmin)
admin.site.register(EventImage, EventImageAdmin)
