from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.base.views.widget_view import WidgetViewSet, upload_widget_file

router = DefaultRouter()

urlpatterns = [
]

urlpatterns += router.urls
