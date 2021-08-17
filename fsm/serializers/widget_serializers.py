from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import Game, Video, Image, Description, Problem, SmallAnswerProblem, SmallAnswer, BigAnswer, \
    MultiChoiceProblem, Choice, MultiChoiceAnswer, UploadFileProblem, BigAnswerProblem, UploadFileAnswer
from fsm.serializers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, ChoiceSerializer, \
    UploadFileAnswerSerializer, MultiChoiceSolutionSerializer
from fsm.serializers.validators import multi_choice_answer_validator


class WidgetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super().create({'creator': self.context.get('user', None), **validated_data})

    # class Meta:
    #     model = Widget
    #     fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of']
    #     read_only_fields = ['id', 'creator', 'duplication_of']


class GameSerializer(WidgetSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class VideoSerializer(WidgetSerializer):
    class Meta:
        model = Video
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ImageSerializer(WidgetSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'creator', 'duplication_of']


class DescriptionSerializer(WidgetSerializer):
    class Meta:
        model = Description
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text']
        read_only_fields = ['id', 'creator', 'duplication_of']


class ProblemSerializer(WidgetSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'required']
        read_only_fields = ['id', 'creator', 'duplication_of']


class SmallAnswerProblemSerializer(WidgetSerializer):
    solution = SmallAnswerSerializer()

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'required', 'solution']
        read_only_fields = ['id', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        serializer = SmallAnswerSerializer(data={'problem': instance,
                                                 'is_final_answer': True,
                                                 'is_solution': True,
                                                 **solution})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return instance


class BigAnswerProblemSerializer(WidgetSerializer):
    solution = BigAnswerSerializer()

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'required', 'solution']
        read_only_fields = ['id', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        serializer = BigAnswerSerializer(data={'problem': instance,
                                               'is_final_answer': True,
                                               'is_solution': True,
                                               **solution})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return instance


class MultiChoiceProblemSerializer(WidgetSerializer):
    choices = ChoiceSerializer(many=True)
    solution = serializers.ListField(child=serializers.IntegerField(min_value=0), allow_empty=True, allow_null=False,
                                     required=True, write_only=True)

    class Meta:
        model = MultiChoiceProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
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

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        choices = validated_data.pop('choices')
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        # used direct creation instead of serializer.save() for fewer db transactions
        choice_objects = [Choice.objects.create(**{'problem': instance, **c}) for c in choices]
        multi_choice_solution = MultiChoiceAnswer.objects.create(**{'problem': instance,
                                                                    'is_final_answer': True,
                                                                    'is_solution': True,
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
            choices_raw = data.pop('choices')
            choices = [{"text": c} for c in choices_raw]
            data['choices'] = choices
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['solution'] = MultiChoiceSolutionSerializer(instance.solution).to_representation(
            instance.solution)
        return representation


class UploadFileProblemSerializer(WidgetSerializer):
    solution = serializers.PrimaryKeyRelatedField(queryset=UploadFileAnswer.objects.all(), required=False)

    class Meta:
        model = UploadFileProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'required', 'solution']
        read_only_fields = ['id', 'creator', 'duplication_of']

    def validate_solution(self, solution):
        if solution.problem is not None:
            raise ParseError(serialize_error('4047'))
        elif solution.submitted_by != self.context.get('user', None):
            raise ParseError(serialize_error('4048'))
        return solution

    @transaction.atomic
    def create(self, validated_data):
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        solution.problem = instance
        solution.is_solution = True
        solution.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['solution'] = UploadFileAnswerSerializer().to_representation(instance.solution)
        return representation


class WidgetPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Widget: WidgetSerializer,
        Description: DescriptionSerializer,
        Image: ImageSerializer,
        Video: VideoSerializer,
        Game: GameSerializer,
        # Problem: ProblemSerializer,
        SmallAnswerProblem: SmallAnswerProblemSerializer,
        BigAnswerProblem: BigAnswerProblemSerializer,
        MultiChoiceProblem: MultiChoiceProblemSerializer,
        UploadFileProblem: UploadFileProblemSerializer,
    }

    resource_type_field_name = 'widget_type'
