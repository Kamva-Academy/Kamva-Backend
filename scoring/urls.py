from django.urls import include, path

from rest_framework import routers

from scoring.views import ScoreTypeViewSet, ScoreViewSet, CommentViewSet

router = routers.DefaultRouter()

urlpatterns = []

router.register(r'score_type', ScoreTypeViewSet)
router.register(r'score', ScoreViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [
   path('', include(router.urls)),
]

urlpatterns += router.urls