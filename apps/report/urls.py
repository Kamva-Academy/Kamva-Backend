from django.urls import path

urlpatterns = [
    path('export_json/' , export,  name='export_json'),
    path('export_csv/', export_csv, name='export_csv'),
]