from accounts.models import Team
from django.utils import timezone
from datetime import timedelta


class TeamsCache:
    data = {}
    last_calculated = None
    seconds_between = 10

    @classmethod
    def clear(cls):
        cls.last_calculated = None

    @classmethod
    def calc_data(cls):
        teams = Team.objects.all()
        valid_teams = []

        for team in teams:
            if team.is_team_active():
                team_json = {
                    "name": team.group_name,
                    "uuid": team.uuid,
                    "team_id": team.id,
                    "team_members": [{"email": p.member.email, "name": p.member.first_name, "uuid": p.member.uuid}
                                     for p in team.participant_set.all()],
                }
                if team.current_state:
                    current_state = team.current_state
                    team_json['current_state'] = {
                        'state_name': current_state.name,
                        'state_id': team.current_state_id,
                        'fsm_name': current_state.fsm.name,
                        'fsm_id': current_state.fsm_id,
                        'page_id': current_state.page_id
                    }

                    state_history = TeamHistory.objects.filter(team=team, state=current_state).order_by(
                        '-start_time')
                    if state_history:
                        team_json['current_state']['start_time'] = str(state_history[0].start_time)
                    else:
                        team_json['current_state']['start_time'] = ''

                valid_teams.append(team_json)
        return valid_teams

    @classmethod
    def get_data(cls):
        if cls.last_calculated is None or (timezone.now() - cls.last_calculated).seconds > cls.seconds_between:
            cls.data = cls.calc_data()
            cls.last_calculated = timezone.now()
        return cls.data
