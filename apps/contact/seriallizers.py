from rest_framework import serializers
from models import *

class ContactMessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        field = ['object' , 'text', 'email']
