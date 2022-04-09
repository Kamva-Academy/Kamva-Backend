from rest_framework import serializers
from event_metadata.models import StaffInfo, StaffTeam
from accounts.models import User

class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']

class StaffTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTeam
        fields = ['name']

class StaffInfoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    user = StaffUserSerializer()
    team = StaffTeamSerializer(many=True)

    class Meta:
        model = StaffInfo
        fields = ['user', 'registration_form', 'title', 'description', 'team', 'image_url']

    def get_image_url(self, staff_info):
        request = self.context.get('request')
        if bool(staff_info.image):
            image_url = staff_info.image.url
            return request.build_absolute_uri(image_url)
        return None