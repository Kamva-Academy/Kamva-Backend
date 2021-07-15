from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from fsm.models import PlayerHistory
from fsm.serializers.serializers import PlayerHistorySerializer
from fsm.views import permissions as customPermissions

class TeamHistoryView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]
    #permission_classes = [permissions.AllowAny]

    queryset = PlayerHistory.objects.all()
    serializer_class = PlayerHistorySerializer
