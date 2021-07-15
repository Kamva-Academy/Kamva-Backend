from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from fsm.models import RegistrationForm, Article
from fsm.serializers.widget_serializer import WidgetPolymorphicSerializer, WidgetSerializer


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


class ArticleSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = ['id', 'widgets']
        read_only_fields = ['id']


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,
        'Article': ArticleSerializer,

    }

    resource_type_field_name = 'paper_type'
