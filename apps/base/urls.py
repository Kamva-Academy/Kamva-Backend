from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.base.views.widget_view import WidgetViewSet, upload_widget_file

router = DefaultRouter()

urlpatterns = [
    path('widget/upload_widget_file/<int:widget_id>/', upload_widget_file),
]

router.register('widget', WidgetViewSet, basename='widget')

urlpatterns += router.urls
