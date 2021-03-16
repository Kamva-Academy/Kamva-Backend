from fsm.models import PlayerHistory, FSM
from fsm.views.participantviews import get_last_state_in_fsm


def get_member_json_info(member):
    response = {
        "email": member.email,
        "name": member.first_name,
        "is_mentor": member.is_mentor,
        "uuid": member.uuid,
        "phone": member.phone_number,
        "gender": member.gender,
    }

    if member.is_participant:
        pass
        # participant = member.participant
        # response['grade'] = participant.member.grade
        # response['gender'] = participant.member.gender
        # response['city'] = participant.member.city
        # response['school'] = participant.member.school
        # response['accepted'] = participant.accepted
        # response['is_activated'] = participant.is_activated

        # if participant.team:
        #     team = participant.team
        #     response['team'] = participant.team_id
        #     response['team_id'] = participant.team_id
        #     response['team_uuid'] = participant.team.uuid,
        #     response['team_members'] = [
        #         {"email": p.member.email, "name": p.member.first_name, "uuid": p.member.uuid}
        #         for p in team.participant_set.all()]
        #     # TODO curren_state is no longer valid
        #     if participant.team.current_state:
        #         current_state = participant.team.current_state
        #         response['current_state'] = {
        #             'state_name': current_state.name,
        #             'state_id': team.current_state_id,
        #             'fsm_name': current_state.fsm.name,
        #             'fsm_id': current_state.fsm_id,
        #             # 'page_id': current_state.page.id
        #         }
        #         state_history = TeamHistory.objects.filter(team=team, state=current_state).order_by('-start_time')
        #         if state_history:
        #             response['current_state']['start_time'] = str(state_history[0].start_time)
        #         else:
        #             response['current_state']['start_time'] = ''
        #
        #     response['current_states'] = get_team_current_states_json(team)
    return response


def get_team_json_info(team):
    response = {
        "name": team.group_name,
        "uuid": team.uuid,
        "team_id": team.id,
        "team_members": [{"email": p.member.email, "name": p.member.first_name, "uuid": p.member.uuid}
                         for p in team.team_members.all()],
    }

    # TODO current_state is no longer valid
    if team.current_state:
        current_state = team.current_state
        response['current_state'] = {
            'state_name': current_state.name,
            'state_id': team.current_state_id,
            'fsm_name': current_state.fsm.name,
            'fsm_id': current_state.fsm_id,
            # 'page_id': current_state.page.id
        }
        state_history = PlayerHistory.objects.filter(team=team, state=current_state).order_by('-start_time')
        if state_history:
            response['current_state']['start_time'] = str(state_history[0].start_time)
        else:
            response['current_state']['start_time'] = ''

    response['current_states'] = get_team_current_states_json(team)
    return response


def get_team_current_states_json(team):
    states = {}
    for fsm in FSM.objects.filter(active = True):
        current_state = get_last_state_in_fsm(team=team, fsm=fsm)
        if current_state:
            state_info = {
                'state_name': current_state.name,
                'state_id': team.current_state_id,
                'fsm_name': current_state.fsm.name,
                'fsm_id': current_state.fsm_id,
                # 'page_id': current_state.page.id
            }
            state_history = PlayerHistory.objects.filter(team=team, state=current_state).order_by('-start_time')
            if state_history:
                state_info['start_time'] = str(state_history[0].start_time)
            else:
                state_info['start_time'] = ''
            states[fsm.id] = state_info
    return states
