from django.db import models
from apps.base.models import Widget


############ CONTENT ############

class Content(Widget):
    pass


class Description(Content):
    text = models.TextField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Game(Content):
    link = models.URLField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Video(Content):
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Audio(Content):
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Aparat(Content):
    video_id = models.TextField()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Image(Content):
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'
