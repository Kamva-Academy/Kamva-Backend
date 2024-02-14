from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q

from apps.scoring.models import ScoreType
from apps.scoring.serializers.scoretype_serializer import ScoreTypeSerializer


class ScoreTypeViewSet(viewsets.ModelViewSet):
    queryset = ScoreType.objects.all()
    serializer_class = ScoreTypeSerializer

    def list(self, request, *args, **kwargs):
        program_id = request.data.get('program_id')
        queryset = self.queryset.filter(
            Q(programs__in=[program_id]) | Q(is_public=True))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
