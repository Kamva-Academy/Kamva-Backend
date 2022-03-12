from attr import fields
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer
from scoring.models import ScoreType, Score, Comment
from errors.error_codes import serialize_error


class ScoreTypeSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        return super().create({**validated_data})

    class Meta:
        model = ScoreType
        fields = ['score_type', 'papers']


class ScoreSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return super().create({**validated_data})
    
    def update(self, instance, validated_data):
        if 'answer' not in validated_data.keys():
            validated_data['answer'] = instance.answer
        elif validated_data.get('answer', None) != instance.answer:
            raise ParseError(serialize_error('4102')) # not so sure about the error code
        return super(ScoreSerializer, self).update(instance, {**validated_data})

    class Meta:
        model = Score
        fields = ['score_value', 'score_type', 'answer']
        read_only_fields = ['score_type', 'answer']
    
class CommentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return super().create({**validated_data})

    def update(self, instance, validated_data):
        if 'answer' not in validated_data.keys():
            validated_data['answer'] = instance.answer
        elif validated_data.get('answer', None) != instance.answer:
            raise ParseError(serialize_error('4102'))
        return super(CommentSerializer, self).update(instance, {**validated_data})

    class Meta:
        model = Comment
        fields = ['content', 'writer', 'answer']
        read_only_fields = ['writer', 'answer']