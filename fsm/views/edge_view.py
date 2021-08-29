from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from fsm.models import Edge
from fsm.permissions import IsEdgeModifier
from fsm.serializers.fsm_serializers import EdgeSerializer


class EdgeViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    my_tags = ['edge']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except(KeyError, AttributeError):
            return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsEdgeModifier]
        return [permission() for permission in permission_classes]
