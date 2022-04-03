from rest_framework import generics
from event_metadata.serializers import StaffInfoSerializer
from event_metadata.models import StaffInfo

class StaffInfoRetrieveView(generics.ListAPIView):
    serializer_class = StaffInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return StaffInfo.objects.filter(registration_form=pk)
