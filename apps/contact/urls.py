from django.urls import path
from .views import ContactMessageView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('message', ContactMessageView, basename='contact-us')

urlpatterns = []
urlpatterns += router.urls