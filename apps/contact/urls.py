from django.urls import path
from views import ContactMessageView
from rest_framework.routers import DefaultRouter


urlpatterns = []

router = DefaultRouter()
router.register(r'contactmessage',  ContactMessageView , basename='contactmessage')

urlpatterns += router


