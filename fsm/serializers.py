from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from accounts.serializers import PlayerSerializer
from fsm.models import *
from accounts.models import Team
import sys
from django.utils import timezone
class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = '__all__'

class FSMEdgeSerializer(serializers.ModelSerializer):
    #abilities = AbilitySerializer(many=True)
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


class FSMStateGetSerializer(serializers.ModelSerializer):
    outward_edges = FSMEdgeSerializer(many=True)
    inward_edges = FSMEdgeSerializer(many=True)
    class Meta:
        model = FSMState
        fields = '__all__'
        queryset = FSM.objects.filter(active=True)
        instance = FSM.objects.filter(active=True)


class FSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = '__all__'

    def get_validation_exclusions(self):
        exclusions = super(FSMSerializer, self).get_validation_exclusions()
        return exclusions + ['first_state', 'fsm_learning_type', 'fsm_p_type']

#
# class FSMCreatSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FSM
#         fields = ['name', 'type', 'active', ]


class FSMGetSerializer(serializers.ModelSerializer):
    states = FSMStateGetSerializer(many=True)
    class Meta:
        model = FSM
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = '__all__'


class SmallAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmallAnswer
        fields = '__all__'


class BigAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigAnswer
        fields = '__all__'


class MultiChoiceAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiChoiceAnswer
        fields = '__all__'


class UploadFileAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFileAnswer
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
    
    @classmethod
    def get_serializer(cls, model):
        if model == SmallAnswer:
            return SmallAnswerSerializer
        elif model == BigAnswer:
            return BigAnswerSerializer
        elif model == MultiChoiceAnswer:
            return MultiChoiceAnswerSerializer
        elif model == UploadFileAnswer:
            return UploadFileAnswerSerializer

    def to_representation(self, instance):
        serializer = AnswerSerializer.get_serializer(instance.__class__)
        return serializer(instance, context=self.context).data

    @transaction.atomic
    def create(self, validated_data):
        serializerClass = AnswerSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['answer_type']))
        serializer = serializerClass(validated_data)
        return serializer.create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        serializerClass = AnswerSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['answer_type']))
        serializer = serializerClass(validated_data)
        return serializer.update(instance, validated_data)


class ProblemSmallAnswerSerializer(serializers.ModelSerializer):
    answer = SmallAnswerSerializer()

    class Meta:
        model = ProblemSmallAnswer
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        instance = ProblemSmallAnswer.objects.create(**validated_data)
        answer_data['answer_type'] = 'SmallAnswer'
        answer = SmallAnswer.objects.create(**answer_data)
        answer.problem = instance
        answer.save()
    
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['pk'] = instance.pk
        try:
            answer = SmallAnswer.objects.filter(problem=instance)[0]
            validated_data['answer']['pk'] = answer.pk
            answer.delete()
        except:
            pass
        instance.delete()
        instance = self.create(validated_data)
        return instance


class ProblemBigAnswerSerializer(serializers.ModelSerializer):
    answer = BigAnswerSerializer()
    class Meta:
        model = ProblemBigAnswer
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        instance = ProblemBigAnswer.objects.create(**validated_data)
        answer_data['answer_type'] = 'BigAnswer'
        answer = BigAnswer.objects.create(**answer_data)
        answer.problem = instance
        answer.save()
    
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['pk'] = instance.pk
        try:
            answer = BigAnswer.objects.filter(problem=instance)[0]
            validated_data['answer']['pk'] = answer.pk
            answer.delete()
        except:
            pass
        instance.delete()
        instance = self.create(validated_data)
        return instance


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['text']

    def create(self, validated_data):
        print(validated_data)


class ProblemMultiChoiceSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    answer = MultiChoiceAnswerSerializer()

    class Meta:
        model = ProblemMultiChoice
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        choices_data = validated_data.pop('choices')
        instance = ProblemMultiChoice.objects.create(**validated_data)
        for choice_data in choices_data:
            choice = Choice.objects.create(**choice_data)
            choice.problem = instance
            choice.save()
        answer_data['answer_type'] = 'MultiChoiceAnswer'
        answer = MultiChoiceAnswer.objects.create(**answer_data)
        answer.problem = instance
        answer.save()
    
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):    
        validated_data['pk'] = instance.pk
        choices = Choice.objects.filter(problem=instance)
        index = 0
        for choice in choices:
            try:
                validated_data['choices'][index]['pk'] = choice.pk
            except:
                pass
            choice.delete()
            index+=1    
        try:
            answer = MultiChoiceAnswer.objects.filter(problem=instance)[0]
            validated_data['answer']['pk'] = answer.pk
            answer.delete()
        except:
            pass
        
        instance.delete()
        instance = self.create(validated_data)
        return instance


class ProblemUploadFileAnswerSerializer(serializers.ModelSerializer):
    answer = UploadFileAnswerSerializer()

    class Meta:
        model = ProblemUploadFileAnswer
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        instance = ProblemUploadFileAnswer.objects.create(**validated_data)
        answer_data['answer_type'] = 'UploadFileAnswer'
        answer = UploadFileAnswer.objects.create(**answer_data)
        answer.problem = instance
        answer.save()

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data['pk'] = instance.pk
        try:
            answer = UploadFileAnswer.objects.filter(problem=instance)[0]
            validated_data['answer']['pk'] = answer.pk
            answer.delete()
        except:
            pass
        instance.delete()
        instance = self.create(validated_data)
        return instance


class ProblemSerializer(serializers.ModelSerializer):

    @classmethod
    def get_serializer(cls, model):
        if model == ProblemSmallAnswer:
            return ProblemSmallAnswerSerializer
        elif model == ProblemBigAnswer:
            return ProblemBigAnswerSerializer
        elif model == ProblemMultiChoice:
            return ProblemMultiChoiceSerializer
        elif model == ProblemUploadFileAnswer:
            return ProblemUploadFileAnswerSerializer

    def to_representation(self, instance):
        serializer = ProblemSerializer.get_serializer(instance.__class__)
        return serializer(instance, context=self.context).data

    @transaction.atomic
    def create(self, validated_data):
        serializerClass = ProblemSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):    
        serializerClass = ProblemSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.update(instance, validated_data)


class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = '__all__'
    
    @classmethod    
    def get_serializer(cls, model):
        if model == Game:
            return GameSerializer
        elif model == Video:
            return VideoSerializer
        elif model == Image:
            return ImageSerializer
        elif model == Description:
            return DescriptionSerializer
        elif issubclass(model, Problem):
            return ProblemSerializer.get_serializer(model)

    @transaction.atomic
    def create(self, validated_data):
        serializerClass = WidgetSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):    
        serializerClass = WidgetSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.update(instance, validated_data)
    
    def to_representation(self, instance):
        serializer = WidgetSerializer.get_serializer(instance.__class__)
        return serializer(instance, context=self.context).data


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
        instance = SubmittedAnswer.objects.create(**validated_data)

        serializerClass = AnswerSerializer.get_serializer(getattr(sys.modules[__name__],\
            answer_data['answer_type']))
        serializer = serializerClass(data=answer_data)
        if not serializer.is_valid(raise_exception=True):
            return None
        answer = serializer.create(serializer.validated_data)
        instance.answer = answer
        
        instance.publish_date = timezone.localtime()
        instance.save()
        return instance


class FSMStateSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True)

    class Meta:
        model = FSMState
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('widgets')
        instance = FSMState.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('widgets')
        validated_data.pop('fsm')
        validated_data['pk'] = instance.pk
        instance.delete()
        instance = self.create(validated_data)
        return instance


class FSMStateGetSerializer(serializers.ModelSerializer):
    outward_edges = FSMEdgeSerializer(many=True)
    inward_edges = FSMEdgeSerializer(many=True)
    widgets = WidgetSerializer(many=True)

    class Meta:
        model = FSMState
        fields = '__all__'
        queryset = FSM.objects.filter(active=True)
        instance = FSM.objects.filter(active=True)


class CurrentStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSMState
        fields = ['id', 'name']

# class WhiteboardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FSMPage
#         fields = ['init_whiteboard']


class TeamHistorySerializer(serializers.ModelSerializer):
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
        exclude = ('start_time', )


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
    current_state = FSMStateGetSerializer()

    class Meta:
        model = PlayerWorkshop
        fields = ['id', 'player', 'current_state', 'last_visit']
