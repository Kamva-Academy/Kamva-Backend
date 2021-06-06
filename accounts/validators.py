from rest_framework import serializers

from errors.error_codes import serialize_error


def phone_number_validator(phone_number):
    if not phone_number.isdigit():
        raise serializers.ValidationError(serialize_error('4000'))
    elif len(phone_number) < 10:
        raise serializers.ValidationError(serialize_error('4001'))
    return phone_number


def grade_validator(grade):
    if grade < 0 or grade > 12:
        raise serializers.ValidationError(serialize_error('4012'))
    return grade
