from django.urls import include, path
from rest_framework import routers
from apps.scoring.views import ScoreTypeViewSet, ScoreViewSet, CommentViewSet
from apps.scoring.views import get_answer_scores_and_comments, set_answer_score, create_comment

router = routers.DefaultRouter()

router.register(r'score_type', ScoreTypeViewSet)
router.register(r'score', ScoreViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [
    path('set_answer_score/', set_answer_score),
    path('get_answer_scores_and_comments/', get_answer_scores_and_comments),
    path('create_comment/', create_comment),
    path('/', include(router.urls)),
]

urlpatterns += router.urls
