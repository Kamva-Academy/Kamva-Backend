import os
import re
import datetime
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error

from apps.scoring.serializers.cost_serializer import CostSerializer
from apps.scoring.serializers.reward_serializer import RewardSerializer
from apps.fsm.models import DetailBoxWidget, Player, Game, Video, Image, TextWidget, Problem, SmallAnswerProblem, MultiChoiceProblem, Choice, UploadFileProblem, BigAnswerProblem, State, Hint, \
    Widget, Team, Aparat, Audio
from apps.fsm.serializers.answer_serializers import SmallAnswerSerializer, ChoiceSerializer, \
    UploadFileAnswerSerializer


def add_datetime_to_filename(file):
    filename, extension = os.path.splitext(file.name)
    file.name = f'{filename}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}{extension}'
    return file

########### WIDGET ###########


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()
    cost = CostSerializer(required=False)
    reward = RewardSerializer(required=False)

    def get_hints(self, obj):
        from apps.fsm.serializers.paper_serializers import WidgetHintSerializer
        return WidgetHintSerializer(obj.hints if hasattr(obj, 'hints') else [], many=True).data

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
            url = self.context.get('request').get_full_path(
            ) if self.context.get('request') else ""
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


########### CONTENT ###########

class GameSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(GameSerializer, self).create({'widget_type': Widget.WidgetTypes.Game, **validated_data})

    class Meta:
        model = Game
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class VideoSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(VideoSerializer, self).create({'widget_type': Widget.WidgetTypes.Video, **validated_data})

    class Meta:
        model = Video
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class AudioSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(AudioSerializer, self).create({'widget_type': Widget.WidgetTypes.Audio, **validated_data})

    class Meta:
        model = Audio
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class AparatSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(AparatSerializer, self).create({'widget_type': Widget.WidgetTypes.Aparat, **validated_data})

    class Meta:
        model = Aparat
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'video_id', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ImageSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(ImageSerializer, self).create({'widget_type': Widget.WidgetTypes.Image, **validated_data})

    class Meta:
        model = Image
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class TextWidgetSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(TextWidgetSerializer, self).create(
            {'widget_type': Widget.WidgetTypes.TextWidget, **validated_data})

    class Meta:
        model = TextWidget
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'text', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of']


class DetailBoxWidgetSerializer(WidgetSerializer):
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        from apps.fsm.serializers.paper_serializers import PaperSerializer
        return PaperSerializer(obj.details).data

    def to_internal_value(self, data):
        from apps.fsm.serializers.paper_serializers import PaperSerializer
        details_serializer = PaperSerializer(data=data.get('details'))
        details_serializer.is_valid(raise_exception=True)
        details_object = details_serializer.save()
        data = super().to_internal_value(data)
        data['details'] = details_object
        return data

    def create(self, validated_data):
        return super(DetailBoxWidgetSerializer, self).create(
            {'widget_type': Widget.WidgetTypes.DetailBoxWidget, **validated_data})

    class Meta:
        model = DetailBoxWidget
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'title', 'details', 'hints', 'cost', 'reward']
        read_only_fields = ['id', 'creator', 'duplication_of', 'details']

########### QUESTIONS ###########


class SmallAnswerProblemSerializer(WidgetSerializer):
    correct_answer = SmallAnswerSerializer(required=False)

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'correct_answer', 'solution', 'hints', 'cost', 'reward', 'be_corrected']
        read_only_fields = ['id', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        has_answer = 'correct_answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('correct_answer')
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
        has_answer = 'correct_answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('correct_answer')
        instance = super().update(instance, {**validated_data})
        if has_answer:
            answer_object = instance.correct_answer
            if answer_object:
                answer_object.text = answer['text']
                answer_object.save()
            else:
                serializer = SmallAnswerSerializer(
                    data={'problem': instance, 'is_final_answer': True, 'is_correct': True, **answer})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('user')
        if hasattr(instance.paper, 'fsm') and user and not user in instance.paper.fsm.mentors.all():
            del representation['correct_answer']
        return representation


class BigAnswerProblemSerializer(WidgetSerializer):

    class Meta:
        model = BigAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution', 'hints', 'cost', 'reward', 'be_corrected']
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
                  'required', 'max_choices', 'choices', 'hints', 'cost', 'reward', 'be_corrected']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        multi_choice_question_instance = super().create(
            {'widget_type': Widget.WidgetTypes.MultiChoiceProblem, **validated_data})
        choices_instances = [Choice.create_instance(multi_choice_question_instance, choice_data)
                             for choice_data in choices_data]
        multi_choice_question_instance.choices.add(*choices_instances)
        return multi_choice_question_instance

    def update(self, question_instance, validated_data):
        choices_data = validated_data.pop('choices')

        # remove deleted choices
        for choice in question_instance.choices.all():
            is_there = False
            for choice_data in choices_data:
                if choice_data['id'] == choice.id:
                    is_there = True
            if not is_there:
                choice.delete()

        for choice_data in choices_data:
            if question_instance.choices and question_instance.choices.filter(id=choice_data.get('id')):
                # update changed choices
                choice_instance = question_instance.choices.get(
                    id=choice_data.get('id'))
                for attr, value in choice_data.items():
                    setattr(choice_instance, attr, value)
                choice_instance.save()
            else:
                # create new choices
                choice_instance = Choice.create_instance(
                    question_instance, choice_data)
                question_instance.choices.add(choice_instance)

        # update question self
        for attr, value in validated_data.items():
            setattr(question_instance, attr, value)

        question_instance.save()
        return question_instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('user')
        if hasattr(instance.paper, 'fsm') and user and not user in instance.paper.fsm.mentors.all():
            for choice in representation['choices']:
                del choice['is_correct']
        return representation


class UploadFileProblemSerializer(WidgetSerializer):

    class Meta:
        model = UploadFileProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution', 'hints', 'cost', 'reward', 'be_corrected']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def validate_answer(self, answer):
        if answer.problem is not None:
            raise ParseError(serialize_error('4047'))
        elif answer.submitted_by != self.context.get('user', None):
            raise ParseError(serialize_error('4048'))
        return answer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.correct_answer and not instance.paper.is_exam:
            representation['correct_answer'] = UploadFileAnswerSerializer(
            ).to_representation(instance.correct_answer)
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
    TextSerializer = TextWidgetSerializer(required=False)
    SmallAnswerProblemSerializer = SmallAnswerProblemSerializer(required=False)
    BigAnswerProblemSerializer = BigAnswerProblemSerializer(required=False)
    MultiChoiceProblemSerializer = MultiChoiceProblemSerializer(required=False)
    UploadFileProblemSerializer = UploadFileProblemSerializer(required=False)
