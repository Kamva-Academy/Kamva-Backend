from rest_framework import serializers
from event_metadata.models import StaffInfo, StaffTeam

class StaffTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTeam
        fields = ['name']

class StaffInfoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    team = StaffTeamSerializer(many=True)

    class Meta:
        model = StaffInfo
        fields = ['registration_form', 'title', 'description', 'team', 'image_url']

    def get_image_url(self, staff_info):
        request = self.context.get('request')
        if bool(staff_info.image):
            image_url = staff_info.image.url
            return request.build_absolute_uri(image_url)
        return None