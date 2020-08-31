def team_change_current_state(team, state):
    team.current_state = state
    team.save()
