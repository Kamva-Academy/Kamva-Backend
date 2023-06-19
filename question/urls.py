from django.urls import path
from rest_framework.routers import DefaultRouter

from question.views.answer_view import UploadAnswerViewSet, AnswerViewSet

router = DefaultRouter()

urlpatterns = [
]

router.register(r'upload_answer', UploadAnswerViewSet,
                basename='upload_answer')
router.register(r'answers', AnswerViewSet, basename='answers')

urlpatterns += router.urls
