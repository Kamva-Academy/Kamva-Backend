from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import activate, ChangePass, UploadAnswerView, UserInfo, TeamInfo, SendVerificationCode, GetTeamData, \
    ChangePassword, RegistrationInfo, VerifyDiscount, UserViewSet, Login, InstituteViewSet, StudentshipViewSet, \
    ProfileViewSet, PaymentViewSet

urlpatterns = [
    path('accounts/verification_code/', SendVerificationCode.as_view(), name="send_verification_code"),
    path('accounts/login/', Login.as_view(), name='create_token'),
    path('accounts/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('accounts/change_pass/', ChangePassword.as_view(), name="logout"),

    # path('registration-info/', RegistrationInfo.as_view(), name="registration_info"),

    # path('pay/', PayView.as_view(), name="pay"),
    # path('pay/verify-payment/', VerifyPayView.as_view(), name="verify-payment"),
    # # path('groupSignup/', GroupSignup.as_view(), name="group_signup"),
    # path('teamdata/', GetTeamData.as_view(), name="get_team_data"),
    # # path('changePass/', ChangePass.as_view(), name="change_password"),
    # path('changepass/', ChangePassword.as_view(), name='change_password'),
    # path('answerFile/', UploadAnswerView.as_view()),
    # re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #         activate, name='activate'),
    # path('userInfo/', UserInfo.as_view(), name="user_info"),
    # path('teamInfo/', TeamInfo.as_view(), name="team_info"),
    # path('teams/', Teams.as_view(), name="teams"),
    # path('verify-discount/', VerifyDiscount.as_view(), name="verify_discount"),
]

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='accounts')
router.register(r'institutes', InstituteViewSet, basename='institutes')
router.register(r'profile', ProfileViewSet, basename='profiles')
router.register(r'studentship', StudentshipViewSet, basename='studentships')
router.register(r'payment', PaymentViewSet, basename='merchandises')
urlpatterns += router.urls
