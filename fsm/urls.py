from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.pageview import *
from .views.fsmview import *
from .views.fsmstateview import *
from .views.fsmedgeview import *
from .views.abilityview import *

router = DefaultRouter()
router.register('page', FSMPageView)
router.register('page/<int:pk>', FSMPageView)
router.register('fsm', FSMView)
router.register('fsm/<int:pk>', FSMView)
router.register('state', FSMStateView)
router.register('state/<int:pk>', FSMStateView)
router.register('edge', FSMEdgeView)
router.register('edge/<int:pk>', FSMEdgeView)
router.register('ability', AbilityView)
router.register('ability/<int:pk>', AbilityView)
urlpatterns = [
]

urlpatterns += router.urls