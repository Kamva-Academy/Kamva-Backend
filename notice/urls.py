from django.urls import path, include

from notice.views import NoticeAPIView, PushNotificationAPIView

urlpatterns = [
    path('', NoticeAPIView.as_view(), name="notice"),
    path('push/', include([
        path('', PushNotificationAPIView.as_view(), name="push_notice")])),
]