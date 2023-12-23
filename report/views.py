from django.shortcuts import render
# your_app/views.py
from django.http import HttpResponse
from django.core.serializers import serialize
from django.apps import apps
import csv

def export(request):
    app_models = apps.get_models()
    serialized_data_list = []
    for model in app_models:
        queryset = model.objects.all()
        serialized_data = serialize('json', queryset)
        serialized_data_list.append(serialized_data)

    exported_data = "[" + ",".join(serialized_data_list) + "]"

    response = HttpResponse(exported_data, content_type='application/json')

    response['Content-Disposition'] = 'attachment; filename=exported_data.json'

    return response


def export_csv(request):
    app_models = apps.get_models()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=exported_data.csv'
    csv_writer = csv.writer(response)
    for model in app_models:
        fields = [field.name for field in model._meta.fields]
        csv_writer.writerow([f"{model.__name__}_{field}" for field in fields])

    for model in app_models:
        queryset = model.objects.all()
        for row in queryset.values():
            csv_writer.writerow([row[field] for field in row])

    return response