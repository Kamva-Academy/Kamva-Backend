from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied, ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from fsm.models import Event, FSM, RegistrationForm, Article, Hint, Edge, State, Tag
from fsm.serializers.certificate_serializer import CertificateTemplateSerializer
from fsm.serializers.widget_polymorphic import WidgetPolymorphicSerializer


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
        if event is not None and self.context.get('user', None) not in event.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return event

    def validate_fsm(self, fsm):
        if fsm is not None and self.context.get('user', None) not in fsm.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return fsm

    class Meta:
        model = RegistrationForm
        ref_name = 'registration_form'
        fields = ['id', 'min_grade', 'max_grade', 'since', 'till', 'duration', 'is_exam', 'conditions', 'widgets',
                  'event', 'fsm', 'paper_type', 'creator', 'accepting_status', 'certificate_templates',
                  'has_certificate', 'certificates_ready', 'audience_type']
        read_only_fields = ['id', 'creator']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class ArticleSerializer(PaperSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)
    tags = serializers.ListSerializer(required=False, child=serializers.CharField(min_length=1, max_length=100),
                                      allow_null=True, allow_empty=True)

    class Meta:
        model = Article
        ref_name = 'article'
        fields = ['id', 'name', 'description', 'widgets', 'tags', 'is_draft', 'publisher', 'cover_page']
        read_only_fields = ['id', 'creator']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        tags = validated_data.pop('tags') if 'tags' in validated_data.keys() else []
        article = super(ArticleSerializer, self).create({'paper_type': 'Article', 'creator': user, **validated_data})
        for t in tags:
            tag = Tag.objects.filter(name=t).first()
            if tag:
                article.tags.add(tag)
            else:
                tag_serializer = TagSerializer(data={'name': t}, context=self.context)
                if tag_serializer.is_valid(raise_exception=True):
                    article.tags.add(tag_serializer.save())
        article.save()
        return article

    def validate_tags(self, tags):
        if len(tags) > 5:
            raise ValidationError(serialize_error('4106'))
        return tags

    def validate(self, attrs):
        publisher = attrs.get('publisher', None)
        user = self.context.get('user', None)
        if publisher and user not in publisher.admins.all():
            raise PermissionDenied(serialize_error('4105'))

        return super(ArticleSerializer, self).validate(attrs)

    def to_representation(self, instance):
        representation = super(ArticleSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags.all(), context=self.context, many=True).data
        return representation


class HintSerializer(PaperSerializer):
    widgets = WidgetPolymorphicSerializer(many=True, required=False)  # in order of appearance

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super(HintSerializer, self).create({'paper_type': 'Hint', 'creator': user, **validated_data})

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
