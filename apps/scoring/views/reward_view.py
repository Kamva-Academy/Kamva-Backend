from rest_framework import permissions, viewsets
from apps.scoring.models import Reward
from apps.scoring.serializers.reward_serializer import RewardSerializer


class RewardViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context
