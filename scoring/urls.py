from django.urls import path, include
from .views import ScoringAPIView, PlayerScoreHistoryAPIView, PlayerCurrentScoreAPIView


urlpatterns = [
    path('', ScoringAPIView.as_view(), name="scoring"),
    path('<int:transaction_id>', ScoringAPIView.as_view(), name="scoring"),
    path('get_history/', PlayerScoreHistoryAPIView.as_view(), name="score_history"),
    path('get_current/', PlayerCurrentScoreAPIView.as_view(), name="current_score")
]
