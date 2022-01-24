from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.answer_view import UploadAnswerViewSet, AnswerViewSet
from .views.article_view import ArticleViewSet
from .views.event_view import EventViewSet
from .views.fsm_view import *
from .views.edge_view import *
from .views.registration_receipt_view import RegistrationReceiptViewSet
from .views.registration_view import RegistrationViewSet
from .views.certificate_view import CertificateTemplateViewSet, FontViewSet
from .views.state_view import StateViewSet, HintViewSet
from .views.widget_view import *
from .views.team_view import *

router = DefaultRouter()

urlpatterns = []

router.register(r'registration', RegistrationViewSet, basename='registration')
router.register(r'certificate_templates', CertificateTemplateViewSet, basename='certificate_templates')
router.register(r'fonts', FontViewSet, basename='fonts')
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
router.register(r'articles', ArticleViewSet, basename='articles')
urlpatterns += router.urls
