from django.urls import re_path
from workshop.consumers import BoardConsumer

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', BoardConsumer)
]
