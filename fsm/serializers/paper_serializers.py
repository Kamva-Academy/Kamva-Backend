from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import *
from fsm.serializers.widget_serializers import WidgetPolymorphicSerializer, WidgetSerializer


class PaperSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Paper
    #     fields = ['id', 'paper_type', 'widgets']

    @transaction.atomic
    def create(self, validated_data):
        widgets = validated_data.pop('widgets', [])
        instance = super().create({'creator': self.context.get('user', None), **validated_data})
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
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), required=False, allow_null=True)
    fsm = serializers.PrimaryKeyRelatedField(queryset=FSM.objects.all(), required=False, allow_null=True)
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance

# TODO - check if update works or not

    def create(self, validated_data):
        event = validated_data.get('event', None)
        fsm = validated_data.get('fsm', None)
        instance = super(RegistrationFormSerializer, self).create(validated_data)
        if event is not None:
            event.registration_form = instance
            event.save()
        elif fsm is not None:
            fsm.registration_form = instance
            fsm.save()

        return instance

    def validate(self, attrs):
        event = attrs.get('event', None)
        fsm = attrs.get('fsm', None)
        if event is not None and fsm is not None:
            raise ParseError(serialize_error('4022'))
        if event is not None and event.registration_form is not None:
            raise ParseError(serialize_error('4023'))
        if fsm is not None and fsm.registration_form is not None:
            raise ParseError(serialize_error('4024'))
        if fsm is None and event is None:
            raise ParseError(serialize_error('4025'))
        return attrs

    def validate_event(self, event):
        if event is not None and not self.context.get('user', None) in event.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return event

    def validate_fsm(self, fsm):
        if fsm is not None and self.context.get('user', None) in fsm.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return fsm

    class Meta:
        model = RegistrationForm
        ref_name = 'registration_form'
        fields = ['id', 'min_grade', 'max_grade', 'deadline', 'conditions', 'widgets', 'event', 'fsm', 'paper_type',
                  'creator', 'accepting_status']
        read_only_fields = ['id', 'creator']


class ArticleSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)

    class Meta:
        model = Article
        ref_name = 'article'
        fields = ['id', 'widgets']
        read_only_fields = ['id']


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,
        'Article': ArticleSerializer,

    }

    resource_type_field_name = 'paper_type'


class ChangeWidgetOrderSerializer(serializers.Serializer):
    order = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)
