from django.shortcuts import render

from event_metadata.models import StaffInfo, EventImage
from event_metadata.serializers import StaffInfoSerializer, EventImageSerializer
from rest_framework import generics
# Create your views here.

class StaffInfoRetrieveView(generics.ListAPIView):
    serializer_class = StaffInfoSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return StaffInfo.objects.filter(event=pk)

class EventImageRetrieveView(generics.ListAPIView):
    serializer_class = EventImageSerializer
    queryset = EventImage.objects.all()

    def get_queryset(self):
        pk = self.kwargs['pk']
        return EventImage.objects.filter(event=pk)
