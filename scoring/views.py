from django.shortcuts import render
from rest_framework import viewsets
from errors.error_codes import serialize_error
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
