from django.db.models import Manager
from django.db.models import Sum


class ScoringManager(Manager):
    def get_team_total_score(self, player_workshop):
        return self.filter(player_workshop_id=player_workshop.id).annotate(total_score=Sum('score'))

    def get_team_score_history(self, player_workshop):
        return self.filter(player_workshop=player_workshop)
