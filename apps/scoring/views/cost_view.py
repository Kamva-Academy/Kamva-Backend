from rest_framework import permissions, viewsets
from apps.scoring.models import Cost
from apps.scoring.serializers.cost_serializer import CostSerializer


class CostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cost.objects.all()
    serializer_class = CostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

