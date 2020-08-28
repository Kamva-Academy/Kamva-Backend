from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.pageview import *
from .views.fsmview import *
from .views.fsmstateview import *
from .views.fsmedgeview import *
from .views.abilityview import *
from .views.widgetview import *
from .views.problemsmallanswerview import *

router = DefaultRouter()
router.register('page', FSMPageView)                 # !!!!!!!!!!
router.register('page/<int:pk>', FSMPageView)        # !!!!!!!!!
router.register('fsm', FSMView)                      # Done get FSMs with GET or create one with POST
router.register('fsm/<int:pk>', FSMView)             # Done
router.register('state', FSMStateView)               # Done get States with GET or create one with POST
router.register('state/<int:pk>', FSMStateView)      # Done
router.register('edge', FSMEdgeView)                 # Done create or update
router.register('edge/<int:pk>', FSMEdgeView)        # Done
router.register('ability', AbilityView)              # به نظر درست میاد. شاید یه دیلیت هم نیاز داشته باشه.
router.register('ability/<int:pk>', AbilityView)     #
router.register('widget', WidgetView)                # Done
router.register('widget/<int:pk>', WidgetView)       #
router.register('small', SmallView)                  #
router.register('small/<int:pk>', SmallView)         #
urlpatterns = [
]

urlpatterns += router.urls