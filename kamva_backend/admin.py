import csv
import logging

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import path
from django.utils.translation import gettext_lazy
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.accounts.models import User
from errors.error_codes import serialize_error
from apps.fsm.models import RegistrationForm, RegistrationReceipt

logger = logging.getLogger(__name__)


def export(request):
    if request.user.is_staff or request.user.is_superuser:
        ct = request.GET.get('ct', None)
        ids = request.GET.get('ids', '').split(',')
        name = request.GET.get('name', 'untitled')
        fields = request.GET.get('fields', None)

        if not ct:
            return None
        content_type = ContentType.objects.get_for_id(ct)
        objects = content_type.get_all_objects_for_this_type().filter(pk__in=ids)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{name}.csv"'

        writer = csv.writer(response)
        if len(objects) > 0:
            if fields is None:
                fields = list(objects[0].__dict__.keys())[1:-1]
            else:
                fields = fields.split(',')
                l = list(objects[0].__dict__.keys())[1:-1]
                validated_fields = []
                for x in fields:
                    if x in l:
                        validated_fields.append(x)
                fields = validated_fields
            writer.writerow(fields)
        for obj in objects:
            to_be_written = list(
                obj.__dict__[x] if x in obj.__dict__.keys() else '' for x in fields)
            writer.writerow(to_be_written)

        return response
    raise PermissionDenied(serialize_error('4068'))


def export_registration(request):
    if request.user.is_staff or request.user.is_superuser:
        q = request.GET.get('q', None)
        if not q:
            return None
        form = RegistrationForm.objects.get(id=q)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{form.event_or_fsm.name}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['username', 'id', 'first_name', 'last_name', 'phone_number', 'email', 'gender', 'national_code',
             'province', 'city', 'grade', 'school', 'principal', 'status', 'receipt_id', 'is_paid',
             'is_participating'])

        for r in form.registration_receipts.all():
            user = r.user
            school = user.school_studentship.school
            writer.writerow(
                [user.username, user.id, user.first_name, user.last_name, user.phone_number, user.email,
                 user.gender, user.national_code, user.province, user.city, user.school_studentship.grade,
                 school.name if school is not None else None, school.principal_name if school is not None else None,
                 r.status, r.id, r.is_paid, r.is_participating])

        return response
    raise PermissionDenied(serialize_error('4068'))


class MyAdminSite(admin.AdminSite):
    site_header = gettext_lazy('Kamva admin')

    def get_urls(self):
        urls = super(MyAdminSite, self).get_urls()
        urls += [path(r'export/', self.admin_view(export), name='export'), ]
        urls += [path(r'export_registration_data/',
                      self.admin_view(export_registration), name='export_registration')]

        return urls
