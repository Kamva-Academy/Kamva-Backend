from django.db import models

from apps.fsm.models import State


class Link:
    source: str
    target: str

    def __init__(self, source, target):
        self.source = source
        self.target = target

    @staticmethod
    def get_link_from_states(source: State, target: State):
        return Link(source.name, target.name)
