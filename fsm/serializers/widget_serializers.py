import re
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from errors.exceptions import InternalServerError
from fsm.models import Player, Game, Video, Image, Description, Problem, SmallAnswerProblem, SmallAnswer, BigAnswer, \
    MultiChoiceProblem, Choice, MultiChoiceAnswer, UploadFileProblem, BigAnswerProblem, UploadFileAnswer, State, Hint, \
    Paper, Widget, Team, Aparat
from fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, ChoiceSerializer, \
    UploadFileAnswerSerializer, MultiChoiceSolutionSerializer

from fsm.serializers.validators import multi_choice_answer_validator
from scoring.models import Scorable


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)

    def create(self, validated_data):
        return super().create({'creator': self.context.get('user', None), **validated_data})

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
        from fsm.serializers.answer_polymorphic import AnswerPolymorphicSerializer
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
                  'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class VideoSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(VideoSerializer, self).create({'widget_type': Widget.WidgetTypes.Video, **validated_data})

    class Meta:
        model = Video
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class AparatSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(AparatSerializer, self).create({'widget_type': Widget.WidgetTypes.Aparat, **validated_data})

    class Meta:
        model = Aparat
        fields = ['id', 'name', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'video_id']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ImageSerializer(WidgetSerializer):
    link = serializers.URLField(required=False)

    def create(self, validated_data):
        return super(ImageSerializer, self).create({'widget_type': Widget.WidgetTypes.Image, **validated_data})

    class Meta:
        model = Image
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class DescriptionSerializer(WidgetSerializer):
    def create(self, validated_data):
        return super(DescriptionSerializer, self).create(
            {'widget_type': Widget.WidgetTypes.Description, **validated_data})

    class Meta:
        model = Description
        fields = ['id', 'name', 'file', 'paper', 'widget_type',
                  'creator', 'duplication_of', 'text']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ProblemSerializer(WidgetSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required']
        read_only_fields = ['id', 'creator', 'duplication_of']


class SmallAnswerProblemSerializer(WidgetSerializer):
    answer = SmallAnswerSerializer(required=False)

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'answer', 'solution']
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
                serializer = SmallAnswerSerializer(data={'problem': instance, 'is_final_answer': True, 'is_correct': True, **answer})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
        return instance


class BigAnswerProblemSerializer(WidgetSerializer):

    class Meta:
        model = BigAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution']
        read_only_fields = ['id', 'creator', 'duplication_of']


class MultiChoiceProblemSerializer(WidgetSerializer):
    # todo - this is bullshit move it to representation
    choices = ChoiceSerializer(many=True, required=False)
    solution = serializers.ListField(child=serializers.IntegerField(min_value=0), allow_empty=True, allow_null=False,
                                     required=True, write_only=True)

    class Meta:
        model = MultiChoiceProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'max_choices', 'choices', 'solution']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def validate(self, attrs):
        solution = attrs.get('solution', [])
        max_choices = attrs.get('max_choices', 1)
        choices = attrs.get('choices', [])

        multi_choice_answer_validator(solution, max_choices)
        for selection in solution:
            if selection >= len(choices):
                raise ParseError(serialize_error('4021', is_field_error=False))

        return super(MultiChoiceProblemSerializer, self).validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        choices = validated_data.pop('choices')
        has_solution = 'solution' in validated_data.keys()
        if has_solution:
            solution = validated_data.pop('solution')
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.MultiChoiceProblem, **validated_data})
        # used direct creation instead of serializer.save() for fewer db transactions
        choice_objects = [Choice.objects.create(
            **{'problem': instance, **c}) for c in choices]
        if has_solution:
            multi_choice_solution = MultiChoiceAnswer.objects.create(**{'problem': instance,
                                                                        'is_final_answer': True,
                                                                        'is_correct': True,
                                                                        'submitted_by': self.context.get('user', None),
                                                                        'answer_type': 'MultiChoiceAnswer'})
            choice_selections = [choice_objects[s] for s in solution]
            multi_choice_solution.choices.add(*choice_selections)
            multi_choice_solution.save()
        return instance

    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     validated_data['pk'] = instance.pk
    #     choices = Choice.objects.filter(problem=instance)
    #     index = 0
    #     for choice in choices:
    #         try:
    #             validated_data['choices'][index]['pk'] = choice.pk
    #         except:
    #             pass
    #         choice.delete()
    #         index += 1
    #     try:
    #         answer = MultiChoiceAnswer.objects.filter(problem=instance)[0]
    #         validated_data['answer']['pk'] = answer.pk
    #         answer.delete()
    #     except:
    #         pass
    #
    #     instance.delete()
    #     instance = self.create(validated_data)
    #     return instance

    def to_internal_value(self, data):
        if 'editable' in self.context and self.context.get('editable') is True:
            if 'choices' in data.keys():
                choices_raw = data.pop('choices')
                choices = [{"text": c} for c in choices_raw]
                data['choices'] = choices
            if 'paper' in data.keys() and not isinstance(data.get('paper'), Paper):
                data['paper'] = get_object_or_404(Paper, id=data.get('paper'))
            # data['paper'] = get_object_or_404(Paper, id=data['paper'])
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.answer and not instance.paper.is_exam:
            representation['answer'] = MultiChoiceSolutionSerializer(instance.answer).to_representation(
                instance.answer)
        return representation


class UploadFileProblemSerializer(WidgetSerializer):    

    class Meta:
        model = UploadFileProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text',
                  'required', 'solution']
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
