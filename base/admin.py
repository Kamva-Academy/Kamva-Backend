from django.contrib import admin

from base.models import *

############ QUESTIONS ############


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    pass


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    pass
