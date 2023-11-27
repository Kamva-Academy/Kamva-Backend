from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error


def multi_choice_answer_validator(choices, max_choices):
    if len(choices) > max_choices:
        raise ParseError(serialize_error('4019', {'max_choices': max_choices, 'len_choices': len(choices)},
                                         is_field_error=False))
    if len(choices) != len(set([choice['id'] for choice in choices])):
        raise ParseError(serialize_error('4020', is_field_error=False))
