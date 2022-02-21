from django.urls import path

from event_metadata.views import EventImageRetrieveView, StaffInfoRetrieveView

urlpatterns = [
    path('<int:pk>/staff_info/', StaffInfoRetrieveView.as_view(), name="staff_infos"),
    path('<int:pk>/images/', EventImageRetrieveView.as_view(), name="event_images"),
]