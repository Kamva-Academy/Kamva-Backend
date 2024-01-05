from django.urls import include, path
from rest_framework import routers
from apps.scoring.views.transaction_view import TransactionViewSet
from apps.scoring.views.scoretype_view import ScoreTypeViewSet

router = routers.DefaultRouter()

router.register(r'transaction', TransactionViewSet)
router.register(r'score_type', ScoreTypeViewSet)

urlpatterns = []

urlpatterns += router.urls
