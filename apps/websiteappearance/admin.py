from django.contrib import admin
from apps.websiteappearance.models import Banner


class BannerAdmin(admin.ModelAdmin):
    model = Banner
    list_display = ['id', 'banner_type', 'is_active']
    list_filter = ['banner_type', 'is_active']


admin.site.register(Banner, BannerAdmin)
