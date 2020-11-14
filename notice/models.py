from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Notice(models.Model):
    class PRIORITY:
        LOW = 3
        MEDIUM = 2
        HIGH = 1

        @classmethod
        def as_list(cls):
            return [getattr(cls, state) for state in vars(cls).keys() if
                    state[0].isupper()]

        @classmethod
        def as_choices(cls):
            return (
                (getattr(cls, state), state.capitalize()) for state in vars(cls).keys() if
                state[0].isupper()
            )

    user = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(choices=PRIORITY.as_choices())
    isPushed = models.BooleanField(default=False)
