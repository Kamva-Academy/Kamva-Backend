from rest_framework.routers import DefaultRouter

from base.views.widget_view import WidgetViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'widget', WidgetViewSet, basename='widgets')

urlpatterns += router.urls
