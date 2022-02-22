from pickletools import optimize
from re import S
from django.db import models

from accounts.models import *
from fsm.models import Event
import PIL

class SimpleTeam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

def event_image_upload_path(instance, filename):
    return f'events/{instance.event.pk}/{filename}/'

class StaffInfo(models.Model):
    account = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='staff_infos')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='staff_infos')
    description = models.TextField(null=True, blank=True)
    team = models.ManyToManyField(SimpleTeam, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.PROTECT, related_name='staff_infos')
    image = models.ImageField(upload_to=event_image_upload_path, blank=True, null=True)

    class Meta:
        unique_together = ['account', 'event']

    def save(self):
        super().save()
        img = PIL.Image.open(self.image.path)
        img.save(self.image.path, optimize=True, quality=85)  

    def __str__(self) -> str:
        return f'{str(self.account)} event:{str(self.event)}'


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=event_image_upload_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self):
        super().save()
        img = PIL.Image.open(self.image.path)
        # width = 2400
        # if img.width < width:
        #     width = img.width
        # height = round(img.height * width / img.width)
        # output_size = (height, width)
        # # img.thumbnail(output_size)
        # img.resize(output_size, PIL.Image.ANTIALIAS)
        img.save(self.image.path, optimize=True, quality=85)    

    def __str__(self) -> str:
        return f'event:{str(self.event)} desc:{self.description}'
