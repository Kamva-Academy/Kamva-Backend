from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = []

# router.register(r'registration', RegistrationViewSet, basename='registration_form')

urlpatterns += router.urls
