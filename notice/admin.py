from django.contrib import admin
from .models import Notice

# Register your models here.


class NoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'timestamp', 'priority']
    list_filter = ['priority']
    list_display_links = ['id']


admin.site.register(Notice, NoticeAdmin)
