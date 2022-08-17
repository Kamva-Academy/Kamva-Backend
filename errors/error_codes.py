import logging

from rest_framework.exceptions import ValidationError

from workshop_backend.settings.base import SMS_CODE_LENGTH

logger = logging.getLogger(__name__)

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
               '4031': 'only institutes\'s admins can create events / fsm',
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
               '4042': 'given code can\'t be used anymore, it has been used before',
               '4043': 'given merchandise is not active',
               '4044': 'you haven\'t registered for this event/fsm',
               '4045': 'you registration has not been accepted yet for this event/fsm',
               '4046': 'you have already purchased this merchandise successfully',
               '4047': 'this file answer has already been associated with a problem',
               '4048': 'you can\'t make others\' answers a solution to your own problems, not here & not in real life',
               '4049': 'you can\'t submit others\' answers to your problems',
               '4050': 'you can\'t make a team when you are not registered / not accepted / not paid',
               '4051': 'you already have an active team membership, you can\'t create a new team unless you don\'t '
                       'have any active team membership',
               '4052': 'given registration receipt (user) does not belong to this team\'s event / fsm',
               '4053': 'user already has an active team membership',
               '4054': 'user has already been invited to this team',
               '4055': 'you can\'t add an unregistered user to a team',
               '4056': 'you can\'t revoke an accepted invitation',
               '4057': 'studentship data incomplete',
               '4058': 'you must provide your gender',
               '4059': 'team member capacity is full',
               '4060': 'only team heads can revoke invitations',
               '4061': 'only registration form modifiers can validate receipts',
               '4062': 'user\'s document is not verified yet',
               '4063': 'no invitee data is given',
               '4064': 'no team is given',
               '4065': 'no receipt found for given username',
               '4066': 'you can\'t create discount code for a merchandise you don\'t own',
               '4067': 'neither username nor user_id is given',
               '4068': 'only admin can export data',
               '4069': 'fsms inside events can\'t have merchandise or registration forms',
               '4070': 'fsm holder should be the same as event holder',
               '4071': 'fsm_p_type must be the same as event type (hybrid & team are the same)',
               '4072': 'team size must be the same as event team size',
               '4073': 'creator must be a modifier of event in order to add fsm to event',
               '4074': 'team based event must have team_size > 0 and vise versa',
               '4075': 'you are not this fsm\'s mentor, only mentors can add or edit states, edges & widgets ',
               '4076': 'tail & head of an edge must be from same fsms',
               '4077': 'fsm can\'t have registration form when its event has registration form too',
               '4078': 'user has no team, it\'s unavailable to enter team based fsms without team',
               '4079': 'no valid registration found for given fsm / event',
               '4080': 'invalid key',
               '4081': 'player history not found',
               '4082': 'player not found',
               '4083': 'player current state and edge tail/head must be the same to move forward/backward on edge',
               '4084': 'other teammates are already trying to move you to next state',
               '4085': 'edge / fsm is locked',
               '4086': 'invalid move',
               '4087': 'unable to move on a hidden edge, only mentors can move you on hidden edges, contact them!',
               '4088': 'no one in this team has entered this fsm',
               '4089': 'only team head can move team',
               '4090': 'given receipt is not a member of this team',
               '4091': 'you are not this form\'s modifier and hence can\'t add any certificate templates',
               '4092': 'pdf must contain only one page',
               '4093': 'certificate template must be only of pdf type or image',
               '4094': 'coordinates for name must be inside the page',
               '4095': 'no certificate template has been found for you in this event/fsm',
               '4096': 'unable to create certificate, contact event holder',
               '4097': 'you have to activate certificate for your event/fsm in order to create a certificate template',
               '4098': 'either this event/fsm doesn\'t have any certificates or they are not ready yet',
               '4099': 'pdf certificate generation is not supported yet',
               '4100': 'registration not started yet.',
               '4101': 'widget and answer problem must be the same',
               '4102': 'you can\'t edit an answer\'s problem once it is created',
               '4103': 'user has already been registered',
               '4104': 'it\'s not the time to upload an answer for this problem',
               '4105': 'you can\'t publish on an institute\'s page that you are not one of its admins',
               '4106': 'maximum number of tags for an article is 5',
               '4107': 'batch registration file must be .csv',
               '4108': 'user didn\'t pass entrance criteria for this fsm',
               '4109': 'this course is not available for your gender',
               '4110': 'you can\'t invite the same person twice',

               '5000': 'sending SMS failed',
               '5001': 'zarinpal request failed, contact with support',
               '5002': 'given registration form is illegal, a form must either associate with an event or a fsm',
               '5003': 'given merchandise is illegal, a merch must be either for an event or a fsm',
               '5004': 'each event/fsm must have a registration form, given one doesn\'t',
               '5005': 'user was not mentor'
               }


def serialize_error(code, params=dict(), is_field_error=True):
    msg = errors_dict.get(code, None)
    if type(msg) == str:
        logger.warning(f'{code}')
        returned = {'code': code, 'detail': msg, **params}
    else:
        logger.warning(f'{code}')
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
