from accounts.models import *


def get_staff_info_upload_path(instance, filename):
    return f'registration_form/{instance.registration_form.id}/{filename}'
