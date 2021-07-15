from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer

from accounts.serializers import PlayerSerializer
from errors.error_codes import serialize_error
from fsm.models import *
from accounts.models import Team
import sys
from django.utils import timezone


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = '__all__'


class FSMEdgeSerializer(serializers.ModelSerializer):
    # abilities = AbilitySerializer(many=True)
    class Meta:
        model = FSMEdge
        fields = '__all__'

    '''
    def create(self, validated_data):
        abilities_data = validated_data.pop('abilities')
        instance = FSMEdge.objects.create(**validated_data)
        for ability_data in abilities_data:
            ability = Ability.objects.create(**ability_data)
            ability.edge = instance
            ability.save()
    
        return instance

    def update(self, instance, validated_data):    
        validated_data['pk'] = instance.pk
        abilities = Ability.objects.filter(edge=instance)
        index = 0
        for ability in abilities:
            try:
                validated_data['abilities'][index]['pk'] = ability.pk
            except:
                pass
            ability.delete()
            index+=1
        instance.delete()
        instance = self.create(validated_data)
        return instance
    '''


class FSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = '__all__'


class FSMRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = '__all__'


class CreateFSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = ['name', 'type', 'active', ]


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super().create({'submitted_by': self.context.get('user', None), **validated_data})

    # class Meta:
    #     model = Answer
    #     fields = '__all__'


class SmallAnswerSerializer(AnswerSerializer):
    class Meta:
        model = SmallAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id']


class BigAnswerSerializer(AnswerSerializer):
    class Meta:
        model = BigAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'text']
        read_only_fields = ['id']


class MultiChoiceAnswerSerializer(AnswerSerializer):
    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'choices']
        read_only_fields = ['id']


class UploadFileAnswerSerializer(AnswerSerializer):
    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_solution',
                  'problem', 'answer_file', 'file_name']


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Answer: AnswerSerializer,
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: UploadFileAnswerSerializer
    }

    resource_type_field_name = 'answer_type'


class WidgetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super().create({'creator': self.context.get('user', None), **validated_data})

    # class Meta:
    #     model = Widget
    #     fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of']
    #     read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class GameSerializer(WidgetSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class VideoSerializer(WidgetSerializer):
    class Meta:
        model = Video
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class ImageSerializer(WidgetSerializer):
    class Meta:
        model = Image
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'link']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class DescriptionSerializer(WidgetSerializer):
    class Meta:
        model = Description
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class ProblemSerializer(WidgetSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


class SmallAnswerProblemSerializer(WidgetSerializer):
    solution = SmallAnswerSerializer()

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'solution']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        SmallAnswer.objects.create(**{'problem': instance,
                                      'is_final_answer': True,
                                      'is_solution': True,
                                      'submitted_by': self.context.get('user', None),
                                      **solution})
        return instance


class BigAnswerProblemSerializer(WidgetSerializer):
    solution = BigAnswerSerializer()

    class Meta:
        model = SmallAnswerProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'solution']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']

    @transaction.atomic
    def create(self, validated_data):
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
        BigAnswer.objects.create(**{'problem': instance,
                                    'is_final_answer': True,
                                    'is_solution': True,
                                    'submitted_by': self.context.get('user', None),
                                    **solution})
        return instance


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'problem', ]
        read_only_fields = ['id', 'problem']


class MultiChoiceProblemSerializer(WidgetSerializer):
    choices = ChoiceSerializer(many=True)
    solution = serializers.ListField(child=serializers.IntegerField(min_value=0), allow_empty=False, allow_null=False,
                                     required=True, write_only=True)

    class Meta:
        model = MultiChoiceProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'max_choices', 'choices', 'solution']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']

    def validate(self, attrs):
        solution = attrs.get('solution', [])
        max_choices = attrs.get('max_choices', 1)
        choices = attrs.get('choices', [])

        if len(solution) > max_choices:
            raise ParseError(serialize_error('4019', {'max_choices': max_choices}, is_field_error=False))
        if len(solution) != len(set(solution)):
            raise ParseError(serialize_error('4020', is_field_error=False))
        for selection in solution:
            if selection >= len(choices):
                raise ParseError(serialize_error('4021', is_field_error=False))

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        choices = validated_data.pop('choices')
        solution = validated_data.pop('solution')
        instance = super().create(validated_data)
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
        representation['solution'] = MultiChoiceAnswerSerializer(instance.solution).to_representation(instance.solution)
        return representation


class UploadFileProblemSerializer(WidgetSerializer):
    solution = UploadFileAnswerSerializer()

    class Meta:
        model = UploadFileProblem
        fields = ['id', 'name', 'paper', 'widget_type', 'creator', 'duplication_of', 'text', 'help_text', 'max_score',
                  'solution']
        read_only_fields = ['id', 'paper', 'creator', 'duplication_of']


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


class PaperSerializer(serializers.ModelSerializer):

    @transaction.atomic
    def create(self, validated_data):
        widgets = validated_data.pop('widgets', [])
        instance = super().create(validated_data)
        self.context['editable'] = False
        for w in widgets:
            serializer = WidgetPolymorphicSerializer(data=w, context=self.context)
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['paper'] = instance
                serializer.save()
        return instance


class RegistrationFormSerializer(PaperSerializer):
    min_grade = serializers.IntegerField(required=False, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = serializers.IntegerField(required=False, validators=[MaxValueValidator(12), MinValueValidator(0)])
    conditions = serializers.CharField(required=False, allow_blank=True)
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance

    class Meta:
        model = RegistrationForm
        fields = ['id', 'min_grade', 'max_grade', 'conditions', 'widgets']
        read_only_fields = ['id']


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,

    }

    resource_type_field_name = 'paper_type'


class SubmitedAnswerSerializer(serializers.ModelSerializer):
    xanswer = AnswerSerializer()

    class Meta:
        model = SubmittedAnswer
        fields = '__all__'


class SubmitedAnswerPostSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer()

    class Meta:
        model = SubmittedAnswer
        fields = ['answer', 'problem', 'player']

    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data['answer']
        serializer = SubmitedAnswerPostSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data.pop('answer')
        # type = answer_data['answer_type']
        # if type == 'BigAnswer':
        #     if len(SubmittedAnswer.objects.filter(answer__answer_type=answer_data['answer_type'],
        #                                           answer__biganswer__text=answer_data['text'], player_id=validated_data['player'][''] )) <= 0:
        #         return None
        # elif type == 'SmallAnswer':
        #     if len(SubmittedAnswer.objects.filter(answer__answer_type=answer_data['answer_type'],
        #                                           answer__smallanswer__text=answer_data['text'])) <= 0:
        #         return None
        # elif type == 'MultiChoiceAnswer':
        #     if len(SubmittedAnswer.objects.filter(answer__answer_type=answer_data['answer_type'],answer__multichoiceanswer__text=answer_data['text'],  )) <= 0:
        #         return None

        instance = SubmittedAnswer.objects.create(**validated_data)

        serializer_class = AnswerSerializer.get_serializer(getattr(sys.modules[__name__], answer_data['answer_type']))
        serializer = serializer_class(data=answer_data)
        if not serializer.is_valid(raise_exception=True):
            return None
        answer = serializer.create(serializer.validated_data)
        instance.answer = answer

        instance.publish_date = timezone.localtime()
        instance.save()
        return instance


class HelpStateSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, required=False)

    class Meta:
        model = HelpState
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = '__all__'


class PlayerStateGetSerializer(serializers.ModelSerializer):
    outward_edges = FSMEdgeSerializer(many=True)
    inward_edges = FSMEdgeSerializer(many=True)
    help_states = HelpStateSerializer(many=True)

    class Meta:
        model = MainState
        fields = '__all__'
        # queryset = FSM.objects.filter(active=True)
        # instance = FSM.objects.filter(active=True)


class MainStateSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, required=False)

    class Meta:
        model = MainState
        fields = '__all__'

    def create(self, validated_data):
        if 'widgets' in validated_data:
            validated_data.pop('widgets')
        instance = MainState.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('widgets')
        validated_data.pop('fsm')
        validated_data['pk'] = instance.pk
        instance.delete()
        instance = self.create(validated_data)
        return instance


class MainStateGetSerializer(serializers.ModelSerializer):
    outward_edges = FSMEdgeSerializer(many=True)
    inward_edges = FSMEdgeSerializer(many=True)
    widgets = WidgetSerializer(many=True)
    help_states = HelpStateSerializer(many=True)

    class Meta:
        model = MainState
        fields = '__all__'
        # queryset = FSM.objects.filter(active=True)
        # instance = FSM.objects.filter(active=True)


class CurrentStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainState
        fields = ['id', 'name']


class FSMGetSerializer(serializers.ModelSerializer):
    states = MainStateGetSerializer(many=True)

    class Meta:
        model = FSM
        fields = '__all__'


# class WhiteboardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FSMPage
#         fields = ['init_whiteboard']


class PlayerHistorySerializer(serializers.ModelSerializer):
    answers = SubmitedAnswerSerializer(many=True)

    class Meta:
        model = PlayerHistory
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('answers')
        instance = PlayerHistory.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('answers')
        validated_data['pk'] = instance.pk
        instance.delete()
        instance = self.create(validated_data)
        return instance


# class UserHistorySerializer(serializers.ModelSerializer):
#     answers = SubmitedAnswerSerializer(many=True)
#
#     class Meta:
#         model = UserHistory
#         fields = '__all__'
#
#     def create(self, validated_data):
#         validated_data.pop('answers')
#         instance = UserHistory.objects.create(**validated_data)
#         return instance
#
#     def update(self, instance, validated_data):
#         validated_data.pop('answers')
#         validated_data['pk'] = instance.pk
#         instance.delete()
#         instance = self.create(validated_data)
#         return instance
#

# class ParticipantSerializer(serializers.ModelSerializer):
#     histories = UserHistorySerializer(many=True)
#     #TODO check the fields
#     class Meta:
#         model = Participant
#         fields = '__all__'


class EditEdgesSerializer(serializers.Serializer):
    edges = serializers.ListField(child=FSMEdgeSerializer())
    tail = serializers.IntegerField()


class GetTeamHistorySerializer(serializers.Serializer):
    team = serializers.IntegerField()


# class GetUserHistorySerializer(serializers.Serializer):
#     team = serializers.IntegerField()


class SetFirstStateSerializer(serializers.Serializer):
    fsm = serializers.IntegerField()


class TeamHistorySubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHistory
        exclude = ('start_time',)


class TeamHistoryGoForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerHistory
        exclude = ('start_time', 'grade')


# class UserHistorySubmitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserHistory
#         exclude = ('start_time', )


class TeamUUIDSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()


class GoToTeamSerializer(serializers.Serializer):
    player_workshop = serializers.IntegerField()


class PlayerWorkshopSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    current_state = CurrentStateSerializer()

    # id = serializers.UUIDField()

    class Meta:
        model = PlayerWorkshop
        fields = ['id', 'player', 'current_state', 'last_visit']


class MentorPlayerWorkshopSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    current_state = MainStateGetSerializer()

    class Meta:
        model = PlayerWorkshop
        fields = ['id', 'player', 'current_state', 'last_visit']
