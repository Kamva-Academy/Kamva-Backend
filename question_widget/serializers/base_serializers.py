from base.serializers.widget_serializers import WidgetSerializer
from scoring.serializers.score_serializers import DeliverableSerializer
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error
from scoring.serializers.score_serializers import DeliverableSerializer


class QuestionSerializer(WidgetSerializer):
    pass


class AnswerSerializer(DeliverableSerializer):
    def create(self, validated_data):
        user = self.context.get('user', None)
        validated_data.get('problem').unfinalize_older_answers(user)
        return super().create({'submitted_by': user, **validated_data})

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        if 'problem' not in validated_data.keys():
            validated_data['problem'] = instance.problem
        elif validated_data.get('problem', None) != instance.problem:
            raise ParseError(serialize_error('4102'))
        instance.problem.unfinalize_older_answers(user)
        return super(AnswerSerializer, self).update(instance, {'is_final_answer': True, **validated_data})

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        answer_sheet = self.context.get('answer_sheet', None)
        if answer_sheet is not None and problem is not None and problem.paper is not None:
            if answer_sheet.answer_sheet_of != problem.paper:
                raise ParseError(serialize_error('4027', {'problem.paper': problem.paper,
                                                          'original paper': answer_sheet.answer_sheet_of},
                                                 is_field_error=False))
        return attrs
