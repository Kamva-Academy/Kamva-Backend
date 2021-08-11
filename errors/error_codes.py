from rest_framework.exceptions import ValidationError

from workshop_backend.settings.base import SMS_CODE_LENGTH


errors_dict = {'4000': 'phone number must be digit',
               '4001': 'phone number must have at least 10 digits',
               '4002': f'valid verification code must have {SMS_CODE_LENGTH} digits',
               '4003': 'invalid verification code or phone number',
               '4004': 'a user already submitted with this phone number',
               '4005': 'verification code expired',
               '4006': 'user not submitted with given credentials',
               '4007': 'no credentials were provided',
               '4008': 'no user found with given phone number',
               '4009': 'either your credentials were wrong or your account has been deactivated',
               '4010': 'this institute is has not been approved yet',
               '4011': 'this user already has a studentship',
               '4012': 'grade must be between 0 and 12',
               '4013': 'major is required for high school students',
               '4014': 'non-high school students can\'t have major',
               '4015': 'college students must enter their studying degree',
               '4016': 'given condition has syntax error',
               '4017': 'given number was not a positive integer',
               '4018': 'price must be a multiple of 500 Tomans',
               '4019': 'number of selected choices can\'t be bigger than max choices for this problem',
               '4020': 'selected choices can\'t have repetitions',
               '4021': 'selected choices should be indices of choices',
               '4022': 'a registration form must belong only to an event or fsm not both',
               '4023': 'event already has a registration form',
               '4024': 'fsm already has a registration form',
               '4025': 'registration form must belong to an event or fsm, neither is provided',
               '4026': 'you can\'t edit this entity you are not one of it\'s modifiers',
               '4027': 'provided answer is to a problem not present in this paper',
               '4028': 'this user already has answered this registration form',
               '4029': 'a required problem is unanswered',
               '4030': 'selected choices should be from corresponding problems',
               '4031': 'only institutes\'s admins can create events',
               '4032': 'your grade doesn\'t fit registration criteria',
               '4033': 'you must provide your grade in your profile',
               '4034': 'you must have an active school studentship to register',
               '4035': 'event is full',
               '4036': 'deadline for registration is missed',
               '4037': 'percentage numbers must be between zero and one',
               '4038': 'given discount code doesn\'t belong to this user',
               '4039': 'given discount code has a merchandise, no merchandise provided',
               '4040': 'this discount code is not for this merchandise',
               '4041': 'given code is expired',
               '4042': 'given code is not valid, (maybe used)',




               '5000': 'sending SMS failed'}

def serialize_error(code, params=dict(), is_field_error=True):
    msg = errors_dict.get(code, None)
    if type(msg) == str:
        returned = {'code': code, 'detail': msg, **params}
    else:
        returned = {'code': code, 'detail': ''}

    if is_field_error:
        return returned
    else:
        return {'non_field_errors': [returned]}


class MyValidationError(ValidationError):
    def __init__(self, params):
        super().__init__(params)
        if isinstance(self.detail, list):
            self.detail = self.detail[0]
