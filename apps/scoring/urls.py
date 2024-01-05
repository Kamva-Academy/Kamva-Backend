from rest_framework import routers
from apps.scoring.views.add_scores_to_user import apply_scores_object_on_user
from apps.scoring.views.cost_view import CostViewSet
from apps.scoring.views.reward_view import RewardViewSet
from apps.scoring.views.transaction_view import TransactionViewSet
from apps.scoring.views.scoretype_view import ScoreTypeViewSet
from django.urls import path
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'reward', RewardViewSet)
router.register(r'cost', CostViewSet)
router.register(r'transaction', TransactionViewSet)
router.register(r'score_type', ScoreTypeViewSet)

urlpatterns = [
    path('apply_scores_object_on_user/', apply_scores_object_on_user),
]

urlpatterns += router.urls
