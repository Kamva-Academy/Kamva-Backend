from rest_framework.routers import DefaultRouter
from apps.websiteappearance.views import BannerViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'banners', BannerViewSet)

urlpatterns += router.urls
