from rest_framework import viewsets
from rest_framework import mixins

from fsm.models import *
from rest_framework import permissions
from fsm import permissions as customPermissions
from fsm.serializers.widget_serializers import SmallAnswerProblemSerializer


class SmallView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]

    queryset = SmallAnswerProblem.objects.all()
    serializer_class = SmallAnswerProblemSerializer
