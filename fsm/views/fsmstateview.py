from django.db import transaction
from rest_framework import status

from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework import mixins


from fsm.models import MainState, HelpState, Article
from fsm.serializers.serializers import MainStateSerializer, MainStateGetSerializer, HelpStateSerializer
from fsm.serializers.paper_serializers import ArticleSerializer

from rest_framework import permissions
from fsm import permissions as customPermissions


class MainStateView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]

    queryset = MainState.objects.all()
    serializer_class = MainStateSerializer

    def get_serializer_class(self):
        return MainStateGetSerializer \
            if self.request.method == 'GET' \
            else MainStateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        data['widgets'] = []
        serializer = MainStateSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        instance.save()
        # if 'widgets' in request.data:
        #     widgets_data = request.data['widgets']
        #     for widget_data in widgets_data:
        #         widget = Widget.objects.get(id=widget_data)
        #         widget.state = instance
        #         widget.save()

        response = serializer.to_representation(instance)
        return Response(response, status=status.HTTP_200_OK)


class HelpStateView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, customPermissions.MentorPermission,]

    queryset = HelpState.objects.all()
    serializer_class = HelpStateSerializer

    def get_serializer_class(self):
        return HelpStateSerializer \
            if self.request.method == 'GET' \
            else HelpStateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        # data['widgets'] = []
        serializer = HelpStateSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        instance.save()
        # if 'widgets' in request.data:
        #     widgets_data = request.data['widgets']
        #     for widget_data in widgets_data:
        #         widget = Widget.objects.get(id=widget_data)
        #         widget.state = instance
        #         widget.save()

        response = serializer.to_representation(instance)
        return Response(response, status=status.HTTP_200_OK)


class ArticleView(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.UpdateModelMixin):
    permission_classes = [permissions.AllowAny]
    mentor_permission = [permissions.IsAuthenticated, customPermissions.MentorPermission, ]

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_serializer_class(self):
        return ArticleSerializer \
            if self.request.method == 'GET' \
            else ArticleSerializer

    def get_permissions(self, ):
        if self.request.method == 'GET':
            return [permission() for permission in self.permission_classes]
        else:
            return [permission() for permission in self.mentor_permission]

    @transaction.atomic
    # @permission_classes([permissions.IsAuthenticated, customPermissions.MentorPermission, ])
    def create(self, request, *args, **kwargs):
        data = request.data
        # data['widgets'] = []
        serializer = ArticleSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            data['pk'] = request.data['pk']
        except:
            pass
        instance = serializer.create(data)
        instance.save()
        # if 'widgets' in request.data:
        #     widgets_data = request.data['widgets']
        #     for widget_data in widgets_data:
        #         widget = Widget.objects.get(id=widget_data)
        #         widget.state = instance
        #         widget.save()

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
