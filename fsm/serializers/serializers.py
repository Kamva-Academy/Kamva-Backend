from rest_framework import serializers
from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error


class BatchRegistrationSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate(self, attrs):
        file = attrs.get('file', None)
        if not file.name.endswith('.csv'):
            raise ParseError(serialize_error('4107'))
        return attrs
