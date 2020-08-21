from django.urls import re_path
from workshop.consumers import BoardConsumer, ChatConsumer


websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', BoardConsumer),
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', ChatConsumer),
]
