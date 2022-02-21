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

    def __str__(self) -> str:
        return f'{str(self.account)} event:{str(self.event)}'


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=event_image_upload_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    def save(self, request=False, *args, **kwargs):
        if request and request.FILES.get('image',False):
             self.image.save('filename', self.image, save=True)
        return super(EventImage, self).save(*args, **kwargs)


    # def save(self):
    #     super().save()
    #     img = PIL.Image.open(self.image.path)
    #     if img.height > 250 or img.width > 250:
    #         output_size = (250, 250)
    #     img.thumbnail(output_size)
    #     img.save(self.cover_image.path)    

    def __str__(self) -> str:
        return f'event:{str(self.event)} desc:{self.description}'
    

# TODO: image for event with data compresion