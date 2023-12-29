from django.shortcuts import render
from .models import *
from .seriallizers import ContactMessageSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ContactMessageView(APIView):
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
