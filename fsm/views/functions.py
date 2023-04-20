from rest_framework.exceptions import ParseError

from fsm.models import *
from fsm.serializers.answer_serializers import AnswerSerializer
from fsm.serializers.widget_serializers import WidgetSerializer

logger = logging.getLogger(__name__)


def get_receipt(user, fsm):
    if fsm.registration_form and fsm.event.registration_form:
        raise ParseError(serialize_error('4077'))
    registration_form = fsm.registration_form or fsm.event.registration_form
    return RegistrationReceipt.objects.filter(user=user, answer_sheet_of=registration_form,
                                              is_participating=True).first()


def get_player(user, fsm, receipt):
    return user.players.filter(fsm=fsm, receipt=receipt, is_active=True).first()


def move_on_edge(p, edge, departure_time, is_forward):
    p.current_state = edge.head if is_forward else edge.tail
    p.last_visit = departure_time
    p.save()
    try:
        last_state_history = PlayerHistory.objects.get(player=p, state=edge.tail if is_forward else edge.head, end_time=None)
    except:
        last_state_history = None
    if last_state_history:
        last_state_history.end_time = departure_time
        last_state_history.save()
    PlayerHistory.objects.create(player=p, state=edge.head if is_forward else edge.tail, entered_by_edge=edge,
                                 start_time=departure_time, reverse_enter=not is_forward)

    return p


def get_a_player_from_team(team, fsm):
    head_receipt = team.team_head
    players = Player.objects.filter(fsm=fsm, receipt__in=team.members.all())
    if len(players) <= 0:
        logger.info('no player found for any member of team')
        raise ParseError(serialize_error('4088'))
    else:
        player = players.filter(receipt=head_receipt).first()
        if not player:
            player = players.first()
        return player

def user_change_current_state(participant, state):
    # TODO change_current_state body
    # check if it is in history or next state
    pass


def user_get_current_state(player, fsm):
    try:
        player_workshop = PlayerWorkshop.objects.filter(
            player=player, workshop=fsm).last()
        current_state = player_workshop.current_state
        if current_state is None:
            current_state = fsm.first_state
    except:
        if fsm.fsm_p_type == 'hybrid':
            return None
        PlayerWorkshop.objects.create(workshop=fsm, player=player,
                                      current_state=fsm.first_state, last_visit=timezone.now())
        current_state = fsm.first_state
    return current_state


def current_state_widgets_json(state, player):
    widgets = []
    for widget in state.widgets():
        widgetJson = WidgetSerializer().to_representation(widget)
        # widgetJson.pop('answer', None)
        widgets.append(widgetJson)

        last_answer = SubmittedAnswer.objects.filter(problem_id=widget.id, player=player) \
            .order_by('-publish_date')
        if len(last_answer) > 0:
            submitted_answer = AnswerSerializer().to_representation(
                last_answer[0].xanswer())
            widgetJson['last_submit'] = submitted_answer
        else:
            if 'answer' in widgetJson:
                widgetJson.pop('answer')
    return widgets


def register_individual_workshop(workshop, participant):
    player_workshop = PlayerWorkshop.objects.create(workshop=workshop, player=participant,
                                                    current_state=workshop.first_state, last_visit=timezone.now())
    return player_workshop


def get_player_workshop(player, fsm):
    return PlayerWorkshop.objects.filter(player=player, workshop=fsm).last()


def get_scores_sum(player_workshop):
    pass


def send_signup_email(self, base_url, password=''):
    options = {
        'user': self,
        'base_url': base_url,
        'token': account_activation_token.make_token(self),
        'uid': urlsafe_base64_encode(force_bytes(self.pk))
    }
    if password != '':
        options['password'] = password
    if self.participant.team is not None:
        options['team'] = self.participant.team.id

    html_content = strip_spaces_between_tags(
        render_to_string('auth/signup_email.html', options))
    text_content = re.sub('<style[^<]+?</style>', '', html_content)
    text_content = strip_tags(text_content)
    msg = EmailMultiAlternatives(
        'تایید ثبت‌نام اولیه', text_content, 'Rastaiha <info@rastaiha.ir>', [self.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
