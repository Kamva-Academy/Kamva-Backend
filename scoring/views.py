from rest_framework import viewsets
from rest_framework import status
from django.db import transaction

from rest_framework.response import Response
from rest_framework.decorators import api_view
from fsm.models import Answer
from scoring.models import ScoreType, Score, Comment
from scoring.serializers.score_serializers import ScoreTypeSerializer, ScoreSerializer, CommentSerializer
# Create your views here.


class ScoreTypeViewSet(viewsets.ModelViewSet):
    queryset = ScoreType.objects.all()
    serialize_class = ScoreTypeSerializer


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serialize_class = ScoreSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serialize_class = CommentSerializer


@api_view(["POST"])
@transaction.atomic
def get_answer_scores_and_comments(request):
    answer_id = request.data.get('answer_id')
    paper = Answer.objects.get(id=answer_id).problem.paper
    answer_scores = []
    for score_type in paper.scoreTypes.all():
        score = Score.objects.filter(
            score_type=score_type, answer__id=answer_id)
        item = {
            'type': ScoreTypeSerializer(score_type).data,
            'score': ScoreSerializer(score[0]).data if len(score) > 0 else None
        }
        answer_scores.append(item)

    comments = Comment.objects.filter(answer__id=answer_id)
    comments_serializer = CommentSerializer(data=comments, many=True)
    comments_serializer.is_valid()

    return Response({'comments': comments_serializer.data, 'scores': answer_scores}, status.HTTP_200_OK)


@api_view(["POST"])
@transaction.atomic
def set_answer_score(request):
    answer_id = request.data.get('answer_id')
    answer = Answer.objects.get(id=answer_id)
    score_type_id = request.data.get('score_type_id')
    score_type = ScoreType.objects.get(id=score_type_id)
    value = request.data.get('score')

    score = Score.objects.filter(
        answer__id=answer_id, score_type__id=score_type_id)

    if len(score) > 0:
        score = score[0]
        score.value = value
        score.save()
    else:
        Score(value=value, answer=answer, score_type=score_type).save()

    return Response({'ok'}, status.HTTP_200_OK)


@api_view(["POST"])
@transaction.atomic
def create_comment(request):
    content = request.data.get('content')
    answer_id = request.data.get('answer_id')
    answer = Answer.objects.get(id=answer_id)
    user = request.user
    Comment(content=content, writer=user, answer=answer).save()

    comments = Comment.objects.filter(answer__id=answer_id)
    comments_serializer = CommentSerializer(data=comments, many=True)
    comments_serializer.is_valid()

    return Response(comments_serializer.data, status.HTTP_200_OK)
