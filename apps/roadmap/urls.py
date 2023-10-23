from rest_framework.routers import DefaultRouter
from django.urls import include, path
from rest_framework import routers

from apps.roadmap.views import get_player_taken_path, get_fsm_roadmap

router = DefaultRouter()

urlpatterns = [
    path('get_player_taken_path/', get_player_taken_path),
    path('get_fsm_roadmap/', get_fsm_roadmap),
]

urlpatterns += router.urls
