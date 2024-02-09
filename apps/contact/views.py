from django.shortcuts import render
from .models import *
from .seriallizers import ContactMessageSerializers
from rest_framework import  viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class ContactMessageView(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializers
    permission_classes = [AllowAny]
    def get(self , request):
        data = ContactMessage.object.all()
        serializer = ContactMessageSerializers(data , many=True)
        return Response(serializer.data)
    def Post(self , request):
        serializer = ContactMessageSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
# Create your views here.
