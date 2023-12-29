from django.urls import path
from .views import ContactMessageView
from rest_framework.routers import DefaultRouter

urlpatterns = []

router = DefaultRouter()

urlpatterns = [ 
    path('contactmessage', ContactMessageView.as_view(), name="contactmessage"),
]

urlpatterns += router.urls
