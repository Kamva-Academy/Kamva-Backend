from django.shortcuts import render

# Create your views here.
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from .models import Notice
from .serializer import NoticeSerializer, NoticeBodySerializer, PushNoticeBodySerializer
from rest_framework.response import Response
from .pagination import pagination_result
from rest_framework import permissions
from .exception import BadRequest
from django.shortcuts import get_object_or_404
from fsm.views import permissions as customPermissions
from .service import PushNotificationService



DEFAULT_PAGE_SIZE = 8


class NoticeAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    """
    GET: ?page=1&page_size=20
    """
    def get(self, request):
        page = request.query_params.get('page', '1')
        page_size = request.query_params.get('page_size', DEFAULT_PAGE_SIZE)
        result = Notice.objects.all()
        serialized = NoticeSerializer(result, many=True).data
        return Response(pagination_result(serialized, page, page_size), status=HTTP_200_OK)

    def post(self, request):
        serialized = NoticeBodySerializer(data=request.data)
        if not serialized.is_valid():
            raise BadRequest
        notice = Notice(user=request.user, title=serialized['title'], message=serialized['message'],
                        priority=serialized['priority'])
        notice.save()
        return Response(notice.id, status=HTTP_200_OK)


class PushNotificationAPIView(APIView):
    permission_classes = [customPermissions.MentorPermission]

    def post(self, request):
        serialized = PushNoticeBodySerializer(data=request.data)
        if not serialized.is_valid():
            raise BadRequest

        notice = get_object_or_404(Notice, id=serialized['id'])
        push_notification = PushNotificationService(notice)
        result = push_notification.execute()
        return Response(result, status=HTTP_200_OK)
