from django.urls import path
from event_metadata.views import StaffInfoRetrieveView

urlpatterns = [
    path('form/<int:pk>/staff_infos/', StaffInfoRetrieveView.as_view(), name='form_staff_infos'),
]