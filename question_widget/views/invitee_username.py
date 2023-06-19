from rest_framework import status
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import User

@api_view(["POST"])
@transaction.atomic
def check_username(request):
    username = request.data.get('username')
    user = User.objects.filter(username=username).first()
    if user:
        return Response({'first_name': user.first_name, 'last_name': user.last_name}, status.HTTP_200_OK)
    else:
        return Response({}, status.HTTP_404_NOT_FOUND)
