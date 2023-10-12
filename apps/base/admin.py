from django.contrib import admin

from apps.base.models import *

############ QUESTIONS ############


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    pass


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    pass
