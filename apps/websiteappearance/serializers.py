from rest_framework import serializers
from apps.websiteappearance.models import Banner


class BannerSerializer(serializers.ModelSerializer):
    desktop_image = serializers.SerializerMethodField()
    mobile_image = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['desktop_image', 'mobile_image', 'redirect_to']
        read_only_fields = ['desktop_image', 'mobile_image', 'redirect_to']

    def get_desktop_image(self, obj):
        request = self.context.get('request')
        abs_url = obj.desktop_image.url
        return request.build_absolute_uri(abs_url)

    def get_mobile_image(self, obj):
        request = self.context.get('request')
        abs_url = obj.mobile_image.url
        return request.build_absolute_uri(abs_url)
