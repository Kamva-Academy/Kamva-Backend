from rest_framework import generics
from event_metadata.serializers import StaffInfoSerializer
from event_metadata.models import StaffInfo
from rest_framework.permissions import AllowAny


class StaffInfoRetrieveView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return StaffInfo.objects.filter(registration_form=pk)
