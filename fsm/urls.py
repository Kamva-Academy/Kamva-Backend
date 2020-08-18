from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.pageview import *

router = DefaultRouter()
router.register('page', FSMPageView)
router.register('page/<int:pk>', FSMPageView)

urlpatterns = [
]

urlpatterns += router.urls