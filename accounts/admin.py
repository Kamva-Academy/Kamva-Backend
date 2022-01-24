import logging

from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType

from .models import Purchase, DiscountCode, User, VerificationCode, \
    University, EducationalInstitute, School, SchoolStudentship, AcademicStudentship, Merchandise

logger = logging.getLogger(__name__)

from django.http import HttpResponseRedirect

zero_media_root = 'backend.rastaiha.ir/api/media/'


class CustomUserAdmin(admin.ModelAdmin):
    def verify_school_documents(self, request, queryset):
        # documents = queryset.exclude(
        #     Q(school_studentship__document__isnull=True) | Q(school_studentship__document__exact='')
        # ).values_list('school_studentship', flat=True)

        documents = queryset.values_list('school_studentship', flat=True)

        updated = SchoolStudentship.objects.filter(pk__in=documents).update(is_document_verified=True)
        self.message_user(request, f'{updated} document verified.', messages.SUCCESS)

    def school(self, obj):
        return obj.school_studentship.school

    model = User
    list_display = ['id', 'username', 'phone_number', 'national_code', 'first_name', 'last_name', 'gender', 'province',
                    'city', 'school']
    search_fields = ['username', 'phone_number', 'national_code']
    actions = [verify_school_documents]
    ordering = ['-date_joined']


class CustomSchoolAdmin(admin.ModelAdmin):
    def merge_schools(self, request, queryset):
        schools = len(queryset)
        first = queryset.first()
        for school in queryset.exclude(id=first.id):
            for fsm in school.fsms.all():
                fsm.holder = first
                fsm.save()
            for event in school.events.all():
                event.holder = first
                event.save()
            for studentship in school.students.all():
                studentship.school = first
                studentship.save()
            school.delete()

        self.message_user(request, f'{schools} schools merged.', messages.SUCCESS)

    model = School
    list_display = ['id', 'name', 'province', 'city', 'school_type', 'postal_code', 'address']
    actions = [merge_schools]
    ordering = ['id']


def export_selected_objects(model_admin, request, queryset):
    selected = queryset.values_list('pk', flat=True)
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect(
        f'/api/admin/export/?ct={ct.pk}&ids={",".join(str(pk) for pk in selected)}&name={ct.model}')


admin.site.add_action(export_selected_objects, 'export_selected')
admin.site.register(User, CustomUserAdmin)
admin.site.register(School, CustomSchoolAdmin)
admin.site.register(EducationalInstitute)
admin.site.register(University)
admin.site.register(DiscountCode)
admin.site.register(VerificationCode)
admin.site.register(Purchase)
admin.site.register(SchoolStudentship)
admin.site.register(AcademicStudentship)
admin.site.register(Merchandise)
