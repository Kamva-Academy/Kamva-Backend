from django.apps import AppConfig


class MyFormConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'my_form'
    name = 'apps.my_form'
