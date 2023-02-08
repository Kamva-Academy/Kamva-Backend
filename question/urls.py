from django.urls import include, path
from rest_framework import routers
from question.views.invitee_username import check_username
# from .views.team_view import *

router = routers.DefaultRouter()

urlpatterns = [
    path('check_username/', check_username),
    path('/', include(router.urls)),
]

urlpatterns += router.urls
