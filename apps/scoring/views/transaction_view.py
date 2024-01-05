from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from apps.scoring.models import Transaction
from apps.scoring.serializers.transaction_serializer import TransactionSerializer
from rest_framework.decorators import action


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    @action(detail=False, methods=['post'])
    def get_current_scores(self, request, *args, **kwargs):
        user = request.user
        program_id = request.data.get('program')
        transactions = self.queryset.filter(to=user)
        print(transactions)
        return Response(data={"salam"}, status=status.HTTP_200_OK)
