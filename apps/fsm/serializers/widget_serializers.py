import os
import re
import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from apps.fsm.models import Player, Game, Video, Image, Description, Problem, SmallAnswerProblem, SmallAnswer, BigAnswer, \
    MultiChoiceProblem, Choice, MultiChoiceAnswer, UploadFileProblem, BigAnswerProblem, UploadFileAnswer, State, Hint, \
    Paper, Widget, Team, Aparat, Audio
from apps.fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, ChoiceSerializer, \
    UploadFileAnswerSerializer, MultiChoiceSolutionSerializer

from apps.fsm.serializers.validators import multi_choice_answer_validator
from rest_framework import serializers


def add_datetime_to_filename(file):
    filename, extension = os.path.splitext(file.name)
    file.name = f'{filename}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}{extension}'
    return file


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()

    def get_hints(self, obj):
        from apps.fsm.serializers.paper_serializers import WidgetHintSerializer
        return WidgetHintSerializer(obj.hints, many=True).data

    def create(self, validated_data):
        if validated_data.get('file'):
            validated_data['file'] = add_datetime_to_filename(
                validated_data['file'])
        return super().create({'creator': self.context.get('user', None), **validated_data})

    def update(self, instance, validated_data):
        if validated_data.get('file'):
            validated_data['file'] = add_datetime_to_filename(
                validated_data['file'])
        return super().update(instance, validated_data)

    def validate(self, attrs):
        user = self.context.get('user', None)
        paper = attrs.get('paper', None)
        if isinstance(paper, State):
            if user not in paper.fsm.mentors.all():
                raise ParseError(serialize_error('4075'))
        elif isinstance(paper, Hint):
            if user not in paper.reference.fsm.mentors.all():
                raise ParseError(serialize_error('4075'))

        return super(WidgetSerializer, self).validate(attrs)

    def to_representation(self, instance):
        from apps.fsm.serializers.answer_polymorphic import AnswerPolymorphicSerializer
        representation = super(
            WidgetSerializer, self).to_representation(instance)
        if 'solution' in representation.keys() and instance.paper.is_exam:
            representation.pop('solution')
        if isinstance(instance, Problem):
            user = self.context.get('user', None)

            # TODO: potentially with BUGS!
            url = self.context.get('request').get_full_path()
            if "/fsm/player/" in url:
                matcher = re.search(r'\d+', url)
                player_id = matcher.group()
                user = Player.objects.filter(id=player_id).first().user

            if user and isinstance(instance.paper, State):
                teammates = Team.objects.get_teammates_from_widget(
                    user, instance)
                latest_answer = instance.answers.filter(
                    submitted_by__in=teammates, is_final_answer=True).last()
                if latest_answer:
                    representation['last_submitted_answer'] = AnswerPolymorphicSerializer(
                        instance=latest_answer).to_representation(latest_answer)
        return representation

    # class Meta:
    #     model = Widget
    #     fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of']
    #     read_only_fields = ['id', 'creator', 'duplication_of']


class GameSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(GameSerializer, self).create({'widget_type': Widget.WidgetTypes.Game, **validated_data})

    class Meta:
        model = Game
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class VideoSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(VideoSerializer, self).create({'widget_type': Widget.WidgetTypes.Video, **validated_data})

    class Meta:
        model = Video
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class AudioSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(AudioSerializer, self).create({'widget_type': Widget.WidgetTypes.Audio, **validated_data})

    class Meta:
        model = Audio
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class AparatSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(AparatSerializer, self).create({'widget_type': Widget.WidgetTypes.Aparat, **validated_data})

    class Meta:
        model = Aparat
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'video_id', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ImageSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(ImageSerializer, self).create({'widget_type': Widget.WidgetTypes.Image, **validated_data})

    class Meta:
        model = Image
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class DescriptionSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(DescriptionSerializer, self).create(
            {'widget_type': Widget.WidgetTypes.Description, **validated_data})

    class Meta:
        model = Description
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'text', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ProblemSerializer(WidgetSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']


class SmallAnswerProblemSerializer(WidgetSerializer):
    answer = SmallAnswerSerializer(required=False)

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'answer', 'solution', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        has_answer = 'answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('answer')
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.SmallAnswerProblem, **validated_data})
        if has_answer:
            serializer = SmallAnswerSerializer(data={'problem': instance,
                                                     'is_final_answer': True,
                                                     'is_correct': True,
                                                     **answer})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        has_answer = 'answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('answer')
        instance = super().update(instance, {**validated_data})
        if has_answer:
            answer_object = instance.answer
            if answer_object:
                answer_object.text = answer['text']
                answer_object.save()
            else:
                serializer = SmallAnswerSerializer(
                    data={'problem': instance, 'is_final_answer': True, 'is_correct': True, **answer})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
        return instance


class BigAnswerProblemSerializer(WidgetSerializer):

    class Meta:
        model = BigAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.BigAnswerProblem, **validated_data})
        return instance


class MultiChoiceProblemSerializer(WidgetSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = MultiChoiceProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'max_choices', 'choices', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def create(self, validated_data):
        multi_choice_problem_instance = super().create(
            {'widget_type': Widget.WidgetTypes.MultiChoiceProblem, **validated_data})
        choices_data = validated_data.pop('choices')
        choices_instances = [Choice.objects.create(
            **{'problem': multi_choice_problem_instance, **choice_data}) for choice_data in choices_data]
        multi_choice_problem_instance.choices.add(choices_instances)
        return multi_choice_problem_instance

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices')

        for choice_data in choices_data:
            choice_instance = instance.choices.get(
                id=choice_data.get('id'))
            for attr, value in choice_data.items():
                setattr(choice_instance, attr, value)
            choice_instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UploadFileProblemSerializer(WidgetSerializer):

    class Meta:
        model = UploadFileProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution', 'hints']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def validate_answer(self, answer):
        if answer.problem is not None:
            raise ParseError(serialize_error('4047'))
        elif answer.submitted_by != self.context.get('user', None):
            raise ParseError(serialize_error('4048'))
        return answer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.answer and not instance.paper.is_exam:
            representation['answer'] = UploadFileAnswerSerializer(
            ).to_representation(instance.answer)
        return representation

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.UploadFileProblem, **validated_data})
        return instance


class MockWidgetSerializer(serializers.Serializer):
    GameSerializer = GameSerializer(required=False)
    VideoSerializer = VideoSerializer(required=False)
    AparatSerializer = AparatSerializer(required=False)
    ImageSerializer = ImageSerializer(required=False)
    DescriptionSerializer = DescriptionSerializer(required=False)
    # ProblemSerializer = ProblemSerializer(required=False)
    SmallAnswerProblemSerializer = SmallAnswerProblemSerializer(required=False)
    BigAnswerProblemSerializer = BigAnswerProblemSerializer(required=False)
    MultiChoiceProblemSerializer = MultiChoiceProblemSerializer(required=False)
    UploadFileProblemSerializer = UploadFileProblemSerializer(required=False)
