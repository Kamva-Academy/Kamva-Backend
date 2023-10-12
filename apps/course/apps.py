from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'course'
    name = 'apps.course'
