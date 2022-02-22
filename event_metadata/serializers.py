from attr import field
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail

from event_metadata.models import EventImage, Role, StaffInfo, SimpleTeam



class SimpleTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleTeam
        fields = ['name', 'description']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description']

class StaffInfoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    team = SimpleTeamSerializer(many=True)
    role = RoleSerializer

    class Meta:
        model = StaffInfo
        fields = ['account', 'event', 'description',  'team', 'role', 'image_url']

    def get_image_url(self, staff_info):
        request = self.context.get('request')
        if bool(staff_info.image):
            image_url = staff_info.image.url
            return request.build_absolute_uri(image_url)
        else:
            return None

class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventImage
        fields = ['event', 'image_url', 'description']
    
    def get_image_url(self, event_image):
        request = self.context.get('request')
        if bool(event_image.image):
            image_url = event_image.image.url
            return request.build_absolute_uri(image_url)
        else:
            return None