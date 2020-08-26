from django.contrib.auth.models import User
from rest_framework import serializers
from fsm.models import *
import sys

class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = '__all__'

class FSMEdgeSerializer(serializers.ModelSerializer):
    abilities = AbilitySerializer(many=True)
    class Meta:
        model = FSMEdge
        fields = '__all__'

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

class FSMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FSM
        fields = '__all__'
class FSMGetSerializer(serializers.ModelSerializer):
    states = FSMStateSerializer(many=True)
    class Meta:
        model = FSM
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
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


class ProblemSmallAnswerSerializer(serializers.ModelSerializer):
    answer = SmallAnswerSerializer()
    class Meta:
        model = ProblemSmallAnswer
        fields = '__all__'
    
    def create(self, validated_data):
        answer_data = validated_data.pop('answer')
        instance = ProblemSmallAnswer.objects.create(**validated_data)
        answer = SmallAnswer.objects.create(**answer_data)
        answer.problem = instance
        answer.save()
    
        return instance
    
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

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class ProblemMultiChoiceSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    answer = MultiChoiceAnswerSerializer
    class Meta:
        model = ProblemMultiChoice
        fields = '__all__'

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

    def create(self, validated_data):
        serializerClass = ProblemSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.create(validated_data)
    
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
        elif model == Description:
            return DescriptionSerializer
        elif issubclass(model, Problem):
            return ProblemSerializer.get_serializer(model)
    
    def create(self, validated_data):
        serializerClass = WidgetSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.create(validated_data)
    
    def update(self, instance, validated_data):    
        serializerClass = WidgetSerializer.get_serializer(getattr(sys.modules[__name__],\
            validated_data['widget_type']))
        serializer = serializerClass(validated_data)
        return serializer.update(instance, validated_data)
    
    def to_representation(self, instance):
        serializer = WidgetSerializer.get_serializer(instance.__class__)
        return serializer(instance, context=self.context).data

    
class FSMPageSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True)
    class Meta:
        model = FSMPage
        fields = '__all__'
    
    def create(self, validated_data):
        validated_data.pop('widgets')
        instance = FSMPage.objects.create(**validated_data)
        return instance
    
    def update(self, instance, validated_data):  
        validated_data.pop('widgets')  
        validated_data['pk'] = instance.pk
        instance.delete()
        instance = self.create(validated_data)
        return instance