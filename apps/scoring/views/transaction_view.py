from rest_framework import permissions, viewsets
from rest_framework.response import Response
from apps.scoring.models import ScoreType, Transaction
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
        program_id = request.data.get('program_id')
        transactions = self.queryset.filter(to=user)
        scores = _sum_scores(transactions)
        # reomving scores that doenot belong to this program:
        filtered_scores = {}
        print(scores)
        for score_type_name in scores:
            score_type_object = ScoreType.objects.filter(
                name=score_type_name).first()
            if score_type_object and (score_type_object.programs == program_id or score_type_object.is_public):
                filtered_scores[score_type_name] = scores[score_type_name]
        scores = filtered_scores

        return Response(data=scores)


def _sum_scores(transactions: list[Transaction]):
    scores_dict = {}
    for transaction in transactions:
        scores = transaction.value
        for score_type in scores:
            if not scores_dict.get(score_type):
                scores_dict.update({score_type: 0})
            scores_dict[score_type] += scores[score_type]

    return scores_dict
