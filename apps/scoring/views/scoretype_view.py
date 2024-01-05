from rest_framework import viewsets

from apps.scoring.models import ScoreType
from apps.scoring.serializers.scoretype_serializer import ScoreTypeSerializer


class ScoreTypeViewSet(viewsets.ModelViewSet):
    queryset = ScoreType.objects.all()
    serialize_class = ScoreTypeSerializer
