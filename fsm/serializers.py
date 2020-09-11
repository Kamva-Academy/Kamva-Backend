from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
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

class FSMStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSMState
        fields = '__all__'


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


class FSMGetSerializer(serializers.ModelSerializer):
    states = FSMStateGetSerializer(many=True)
    teams = serializers.IntegerField()
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
        fields = '__all__'

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


class ProblemSerializer(serializers.ModelSerializer):

    @classmethod
    def get_serializer(cls, model):
        if model == ProblemSmallAnswer:
            return ProblemSmallAnswerSerializer
        elif model == ProblemBigAnswer:
            return ProblemBigAnswerSerializer
        elif model == ProblemMultiChoice:
            return ProblemMultiChoiceSerializer

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

    
class FSMPageSerializer(serializers.ModelSerializer):
    state = FSMStateSerializer()
    widgets = WidgetSerializer(many=True)

    class Meta:
        model = FSMPage
        fields = '__all__'
    
    def create(self, validated_data):
        validated_data.pop('widgets')
        validated_data.pop('state')
        instance = FSMPage.objects.create(**validated_data)
        return instance
    
    def update(self, instance, validated_data):  
        validated_data.pop('widgets')
        validated_data['pk'] = instance.pk
        instance.delete()
        instance = self.create(validated_data)
        return instance


class WhiteboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSMPage
        fields = ['init_whiteboard']


class SubmitedAnswerSerializer(serializers.ModelSerializer):
    xanswer = AnswerSerializer()
    class Meta:
        model = SubmitedAnswer
        fields = '__all__'


class SubmitedAnswerPostSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer()
    class Meta:
        model = SubmitedAnswer
        fields = ['answer', 'problem']
    
    @transaction.atomic
    def create(self, validated_data):
        answer_data = validated_data['answer']
        serializer = SubmitedAnswerPostSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data.pop('answer')
        instance = SubmitedAnswer.objects.create(**validated_data)

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

 

class TeamHistorySerializer(serializers.ModelSerializer):
    answers = SubmitedAnswerSerializer(many=True)
    class Meta:
        model = TeamHistory
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('answers')
        instance = TeamHistory.objects.create(**validated_data)
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

class TeamSerializer(serializers.ModelSerializer):
    histories = TeamHistorySerializer(many=True)

    class Meta:
        model = Team
        fields = '__all__'


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
        model = TeamHistory
        exclude = ('start_time', )


class TeamHistoryGoForwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamHistory
        exclude = ('start_time', 'grade')


# class UserHistorySubmitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserHistory
#         exclude = ('start_time', )


class TeamUUIDSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()


class GoToTeamSerializer(serializers.Serializer):
    team = serializers.IntegerField()
