from django.db import models
from accounts.models import *
from fsm.models import RegistrationForm
from PIL import Image

# class StaffTitel(models.Model):
#     name = models.CharField(max_length=64)

#     def __str__(self) -> str:
#         return self.name

class StaffTeam(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


def get_staff_info_upload_path(instance, filename):
    return f'registration_form/{instance.registration_form.id}/{filename}'

class StaffInfo(models.Model):
    account = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='staff_infos')
    registration_form = models.ForeignKey(RegistrationForm, on_delete=models.CASCADE, related_name='staff_infos')
    title = models.CharField(max_length=50, null=True, blank=True)
    team = models.ManyToManyField(StaffTeam, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=get_staff_info_upload_path, null=True, blank=True)

    class Meta:
        unique_together = ['account', 'registration_form']

    def save(self, *args, **kwargs) -> None:
        super().save()
        if bool(self.image):
            image = Image.open(self.image.path)
            image.save(self.image.path,quality=75,optimize=True)

    def __str__(self) -> str:
        return f'{self.account}: {self.title} in {self.team}'

