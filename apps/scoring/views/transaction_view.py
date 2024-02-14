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
    def get_user_current_scores(self, request, *args, **kwargs):
        user = request.user
        program_id = int(request.data.get('program_id'))
        scores = get_user_current_scores(user, program_id)
        return Response(data=scores)


def get_user_current_scores(user, program_id: int):
    transactions = Transaction.objects.filter(to=user)
    scores = sum_transactions(transactions)

    # if no program is specified, return all the scores:
    if program_id == -1:
        return scores

    # reomving scores that doenot belong to this program:
    filtered_scores = {}
    for score_type_name in scores:
        score_type_object = ScoreType.objects.filter(
            name=score_type_name).first()
        if score_type_object and (program_id in [program.id for program in score_type_object.programs.all()] or score_type_object.is_public):
            filtered_scores[score_type_name] = scores[score_type_name]
    return filtered_scores


def sum_transactions(transactions: list[Transaction]):
    scores_dict = {}
    for transaction in transactions:
        scores = transaction.value
        for score_type in scores:
            if not scores_dict.get(score_type):
                scores_dict.update({score_type: 0})
            scores_dict[score_type] += scores[score_type]

    return scores_dict
