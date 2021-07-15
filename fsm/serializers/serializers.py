from rest_framework import serializers

from accounts.serializers import PlayerSerializer
from fsm.models import *
import sys
from django.utils import timezone

from fsm.serializers.answer_serializer import AnswerSerializer
from fsm.serializers.widget_serializer import WidgetSerializer


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


class EditEdgesSerializer(serializers.Serializer):
    edges = serializers.ListField(child=FSMEdgeSerializer())
    tail = serializers.IntegerField()


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


class FSMGetSerializer(serializers.ModelSerializer):
    states = MainStateGetSerializer(many=True)

    class Meta:
        model = FSM
        fields = '__all__'
