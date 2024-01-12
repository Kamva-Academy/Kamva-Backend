from rest_framework import serializers

from apps.fsm.models import ProgramContactInfo


class ProgramContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramContactInfo
        fields = '__all__'
        read_only_fields = ['id']
