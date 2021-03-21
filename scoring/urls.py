from django.urls import path, include
from .views import ScoringAPIView, ScoreboardAPIView, TeamScoreAPIVIEW


urlpatterns = [
    path('', ScoringAPIView.as_view(), name="scoring"),
    path('<int:transaction_id>', ScoringAPIView.as_view(), name="scoring"),
    path('scoreboard/', include([
        path('', ScoreboardAPIView.as_view(), name="scoreboard"),
        path('<int:player_workshop_id>', TeamScoreAPIVIEW.as_view(), name="player_score"),
    ])),
]
