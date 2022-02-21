from django.contrib import admin

from event_metadata.models import StaffInfo, EventImage
# Register your models here.

admin.site.register(StaffInfo)
admin.site.register(EventImage)
