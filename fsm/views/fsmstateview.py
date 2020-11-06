from django.db import transaction
from rest_framework import status

from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import mixins


from fsm.models import FSMState, Widget
from fsm.serializers import FSMStateSerializer, FSMStateGetSerializer

from rest_framework import permissions
from fsm.views import permissions as customPermissions


class FSMStateView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]

    queryset = FSMState.objects.all()
    serializer_class = FSMStateSerializer

    def get_serializer_class(self):
        return FSMStateGetSerializer \
            if self.request.method == 'GET' \
            else FSMStateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        widgets_data = request.data['widgets']
        data = request.data
        data['widgets'] = []
        serializer = FSMStateSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        instance.save()
        for widget_data in widgets_data:
            widget = Widget.objects.get(id=widget_data)
            widget.state = instance
            widget.save()

        response = serializer.to_representation(instance)
        return Response(response, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def get_state_page(request):
#     state_id = request.data['state']
#     try:
#         page = FSMState.objects.get(id = state_id).page
#     except:
#         return Response({"error": "no such a state found"}, status=status.HTTP_400_BAD_REQUEST)
#     serializer = FSMPageSerializer()
#     data = serializer.to_representation(page)
#     return Response(data, status=status.HTTP_200_OK)
