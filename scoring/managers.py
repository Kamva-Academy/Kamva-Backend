from django.db.models import Manager


class ScoringManager(Manager):
    def get_team_total_score(self, player_workshop):
        return self.filter(player_workshop=player_workshop).annotate(total_score=sum('score'))

    def get_team_score_history(self, player_workshop):
        return self.filter(player_workshop=player_workshop)
