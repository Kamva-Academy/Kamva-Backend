from rest_framework import serializers
from rest_framework.exceptions import ParseError
from scoring.models import ScoreType, Score, Comment
from errors.error_codes import serialize_error
from accounts.serializers import UserSerializer
from fsm.serializers.widget_serializers import WidgetSerializer


class ScorableSerializer(WidgetSerializer):
    pass


class DeliverableSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super().create({'deliverer': user, **validated_data})



class ScoreTypeSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return super().create({**validated_data})

    class Meta:
        model = ScoreType
        fields = ['id', 'name']


class ScoreSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return super().create({**validated_data})

    def update(self, instance, validated_data):
        if 'deliverable' not in validated_data.keys():
            validated_data['deliverable'] = instance.deliverable
        elif validated_data.get('deliverable', None) != instance.deliverable:
            # not so sure about the error code
            raise ParseError(serialize_error('4102'))
        return super(ScoreSerializer, self).update(instance, {**validated_data})

    class Meta:
        model = Score
        fields = ['value', 'type', 'deliverable']


class CommentSerializer(serializers.ModelSerializer):
    writer = UserSerializer()

    def create(self, validated_data):
        return super().create({**validated_data})

    def update(self, instance, validated_data):
        if 'deliverable' not in validated_data.keys():
            validated_data['deliverable'] = instance.deliverable
        elif validated_data.get('deliverable', None) != instance.deliverable:
            raise ParseError(serialize_error('4102'))
        return super(CommentSerializer, self).update(instance, {**validated_data})

    class Meta:
        model = Comment
        fields = ['content', 'writer', 'deliverable']
        read_only_fields = ['writer', 'deliverable']

