import logging

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from accounts.models import User
from accounts.serializers import ProfileSerializer

logger = logging.getLogger(__name__)


class ProfileViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProfileSerializer
    my_tags = ['accounts']

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return User.objects.none()
        elif user.is_staff or user.is_superuser or len(user.institutes) > 0 or len(user.events) > 0 or len(user.fsms) > 0:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)