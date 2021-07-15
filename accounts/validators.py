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


def price_validator(price):
    if positive_integer_validator(price) == price:
        if price % 500 == 0:
            return price
        raise serializers.ValidationError(serialize_error('4018'))


def positive_integer_validator(integer):
    if integer > 0 and (integer * 10) % 10 == 0:
        return integer
    else:
        raise serializers.ValidationError(serialize_error('4017'))


def condition_validator(condition):
    # TODO - needs  completion, a valid condition:
    """
    def condition(user):
        # every intended condition
        if user.grade == 9:
            return True
        return False
    condition
    """
    try:
        compile(condition, "condition", "exec")
        return condition
    except SyntaxError:
        raise serializers.ValidationError(serialize_error('4016'))
