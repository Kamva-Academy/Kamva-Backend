import logging

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Studentship
from accounts.serializers import StudentshipSerializer, InstituteSerializer

logger = logging.getLogger(__name__)


# todo - everyone can edit anyone's studentships
class StudentshipViewSet(ModelViewSet):
    parser_classes = [MultiPartParser, ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = StudentshipSerializer
    queryset = Studentship.objects.all()
    my_tags = ['studentship']

    @swagger_auto_schema(responses={200: InstituteSerializer,
                                    403: "error code 4011 for already associating a studentship to user"
                                    })
    @transaction.atomic
    def create(self, request):
        data = request.data
        serializer = StudentshipSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)