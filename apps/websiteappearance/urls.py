from rest_framework.routers import DefaultRouter
from apps.websiteappearance.views import BannerViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'banner', BannerViewSet)

urlpatterns += router.urls
