from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from fsm import permissions as customPermissions
from fsm.models import FSMEdge
from fsm.serializers.serializers import FSMEdgeSerializer


class FSMEdgeView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]
    queryset = FSMEdge.objects.all()
    serializer_class = FSMEdgeSerializer
