
from fsm.models import *
from django.utils import timezone
def team_change_current_state(team, state):
    #fsm change checked
    #create history
    team.current_state = state
    if state and len(TeamHistory.objects.filter(team=team.id, state=state.id)) == 0:
        history = TeamHistory.objects.create(start_time=timezone.localtime(), team=team, state=state)
    team.save()
