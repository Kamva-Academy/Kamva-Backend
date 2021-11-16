from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import Event, FSM, RegistrationForm, Article, Hint, Edge, State
from fsm.serializers.certificate_serializer import CertificateTemplateSerializer
from fsm.serializers.widget_serializers import WidgetPolymorphicSerializer


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
    certificate_templates = CertificateTemplateSerializer(many=True, read_only=True)
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance

    @transaction.atomic
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
        fields = ['id', 'min_grade', 'max_grade', 'since', 'till', 'duration', 'is_exam', 'conditions', 'widgets',
                  'event', 'fsm', 'paper_type', 'creator', 'accepting_status', 'certificate_templates']
        read_only_fields = ['id', 'creator']


class ArticleSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)

    class Meta:
        model = Article
        ref_name = 'article'
        fields = ['id', 'widgets']
        read_only_fields = ['id']


class HintSerializer(PaperSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance

    @transaction.atomic
    def create(self, validated_data):
        return super(HintSerializer, self).create({'paper_type': 'Hint', **validated_data})

    def validate(self, attrs):
        reference = attrs.get('reference', None)
        user = self.context.get('user', None)
        if user not in reference.fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(HintSerializer, self).validate(attrs)

    class Meta:
        model = Hint
        ref_name = 'hint'
        fields = ['id', 'widgets', 'creator', 'reference']
        read_only_fields = ['id', 'creator']


class EdgeSimpleSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super(EdgeSimpleSerializer, self).to_representation(instance)
        representation['str'] = str(instance)
        return representation

    class Meta:
        model = Edge
        fields = '__all__'
        read_only_fields = ['id', 'tail', 'head', 'is_back_enabled', 'min_score', 'cost', 'priority', 'lock',
                            'has_lock', 'is_hidden', 'text']


class StateSerializer(PaperSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance
    hints = HintSerializer(many=True, read_only=True)
    outward_edges = EdgeSimpleSerializer(many=True, read_only=True)
    inward_edges = EdgeSimpleSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        fsm = validated_data.get('fsm', None)
        instance = super(StateSerializer, self).create({'paper_type': 'State', **validated_data})
        if fsm.first_state is None:
            fsm.first_state = instance
            fsm.save()

        return instance

    def validate(self, attrs):
        fsm = attrs.get('fsm', None)
        user = self.context.get('user', None)
        if user not in fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(StateSerializer, self).validate(attrs)

    class Meta:
        model = State
        ref_name = 'state'
        fields = ['id', 'widgets', 'name', 'creator', 'fsm', 'hints', 'inward_edges', 'outward_edges', 'since', 'till',
                  'duration', 'is_exam']
        read_only_fields = ['id', 'creator', 'hints', 'inward_edges', 'outward_edges']


class StateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'fsm', 'since', 'till', 'duration', 'is_exam']
        read_only_fields = ['id', 'name', 'fsm', 'since', 'till', 'duration', 'is_exam']


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,
        'Article': ArticleSerializer,
        'State': StateSerializer,
        'Hint': HintSerializer

    }

    resource_type_field_name = 'paper_type'


class ChangeWidgetOrderSerializer(serializers.Serializer):
    order = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)
