from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from fsm.views import permissions as customPermissions
from fsm.models import Ability

from fsm.serializers.serializers import AbilitySerializer


class AbilityView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]
    queryset = Ability.objects.all()
    serializer_class = AbilitySerializer
