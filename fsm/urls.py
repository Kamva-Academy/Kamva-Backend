from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.answer_view import UploadAnswerViewSet, AnswerViewSet
from .views.event_view import EventViewSet
from .views.fsm_view import *
from .views.fsmstateview import *
from .views.edge_view import *
from .views.registration_receipt_view import RegistrationReceiptViewSet
from .views.registration_view import RegistrationViewSet
from .views.state_view import StateViewSet, HintViewSet
from .views.widget_view import *
from .views.teamhistoryview import *
from .views.team_view import *
from .views.participantviews import *
from .views.mentorviews import *

router = DefaultRouter()
# router.register('page', FSMPageView)
# router.register('page/<int:pk>', FSMPageView)
# router.register('fsm', FSMView)
# router.register('fsm/<int:pk>', FSMView)
# router.register('state', MainStateView)
# router.register('state/<int:pk>', MainStateView)
# router.register('helpstate', HelpStateView)
# router.register('helpstate/<int:pk>', HelpStateView)
# router.register('article', ArticleView)
# router.register('article/<int:pk>', ArticleView)
# router.register('edge', FSMEdgeView)
# router.register('edge/<int:pk>', FSMEdgeView)
# router.register('ability', AbilityView)
# router.register('ability/<int:pk>', AbilityView)
# router.register('widget', WidgetView)
# router.register('widget/<int:pk>', WidgetView)
# router.register('history', TeamHistoryView)
# router.register('history/<int:pk>', TeamHistoryView)
# router.register('team', TeamView)
# router.register('team/<int:pk>', TeamView)
# router.register('small', SmallView)
# router.register('small/<int:pk>', SmallView)
urlpatterns = [
     # path('getcurrentstate/', get_player_current_state),
     # # path('getstatepage/', get_state_),
     # path('gethistory/', get_history),
     # path('sendanswer/', send_answer),
     # path('editedges/', edit_edges),
     # # TODO check if fsm is team or individual
     # path('getteamhistory/', get_team_history),
     # # path('getteamfsmhistory/', get_team_fsm_history),
     # # TODO for individual fsm
     # path('getteamoutwardedges/', get_team_outward_edges),
     # path('usergetteamoutwardedges/', user_get_team_outward_edges),
     # # path('set_first_current_page/', set_first_current_state),
     # path('movetonextstate/', move_to_next_state),
     # path('submitteam/', submit_team),
     # # path('goforward/', team_go_forward),
     # # path('gobackto/', team_go_back_to_state),
     # path('visitteam/', go_to_team),
     # path('requestmentor/', request_mentor),
     # path('get_team/', get_team, name="get_team"),
     #
     # # new ones
     # path('userworkshops/', user_workshops, name="user_workshops"),
     # path('getworkshopsdescription/', user_workshops_description, name="user_workshops_description"),
     # path('workshopplayers/', workshop_players, name="workshop_players"),
     # path('goforward/', player_go_forward_on_edge, name="player_go_forward_on_edge"),
     # path('gobackward/', player_go_backward_on_edge, name="player_go_backward_on_edge"),
     # path('startWorkshop/', start_workshop, name="start_workshop"),
     # path('mentorgetplayerstate/', mentor_get_player_state, name="mentor_get_player_state"),
     # path('pargetplayerstate/', participant_get_player_state, name="participant_get_player_state"),
     # path('getscores/', get_scores, name="get_scores"),
     # path('getproblems/', mentor_get_all_problems, name="mentor_get_all_problems"),
     # path('getsubmissions/', mentor_get_submissions, name="mentor_get_submissions"),
     # path('marksubmission/', mentor_mark_submission, name="mentor_mark_submission"),
     # path('mentorgetplayerstate/', mentor_get_workshop_player, name="mentor_get_workshop_player"),
]

router.register(r'registration', RegistrationViewSet, basename='registration')
router.register(r'event', EventViewSet, basename='events')
router.register(r'receipts', RegistrationReceiptViewSet, basename='receipts')
router.register(r'team', TeamViewSet, basename='teams')
router.register(r'invitations', InvitationViewSet, basename='invitations')
router.register(r'upload_answer', UploadAnswerViewSet, basename='upload_answer')
router.register(r'fsm', FSMViewSet, basename='fsms')
router.register(r'state', StateViewSet, basename='states')
router.register(r'edge', EdgeViewSet, basename='edges')
router.register(r'hint', HintViewSet, basename='hints')
router.register(r'widget', WidgetViewSet, basename='widgets')
router.register(r'player', PlayerViewSet, basename='players')
router.register(r'answers', AnswerViewSet, basename='answers')
urlpatterns += router.urls
