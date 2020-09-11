from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.pageview import *
from .views.fsmview import *
from .views.fsmstateview import *
from .views.fsmedgeview import *
from .views.abilityview import *
from .views.widgetview import *
from .views.problemsmallanswerview import *
from .views.teamhistoryview import *
from .views.teamview import *
from .views.participantviews import *
from .views.mentorviews import *

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
router.register('widget', WidgetView)
router.register('widget/<int:pk>', WidgetView)
# TODO check if fsm is team or individual
router.register('history', TeamHistoryView)
router.register('history/<int:pk>', TeamHistoryView)
router.register('team', TeamView)
router.register('team/<int:pk>', TeamView)
# router.register('small', SmallView)
# router.register('small/<int:pk>', SmallView)
urlpatterns = [
     path('getcurrentpage/', get_current_page),
     path('gethistory/', get_history),
     path('sendanswer/', send_answer),
     path('editedges/', edit_edges),
     # TODO check if fsm is team or individual
     path('getteamhistory/', get_team_history),
     path('getteamfsmhistory/', get_team_fsm_history),
     # TODO for individual fsm
     path('getteamoutwardedges/', get_team_outward_edges),
     path('set_first_current_page/', set_first_current_page),
     path('movetonextstate/', move_to_next_state),
     path('submitteam/', submit_team),
     path('go/', submit_team),
     path('gototeam/', go_to_team),
     path('requestmentor/', request_mentor)
]

urlpatterns += router.urls