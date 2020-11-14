from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class NoticeBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('title', 'message', 'priority')


class PushNoticeBodySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
