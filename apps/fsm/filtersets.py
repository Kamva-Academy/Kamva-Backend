from django.db.models import Q
from django_filters.rest_framework import FilterSet, DateTimeFromToRangeFilter, \
    ModelChoiceFilter, NumberFilter

from apps.fsm.models import Answer, Team


def filter_not_empty(queryset, name, value):
    lookup = '__'.join([name, 'isnull'])
    return queryset.filter(**{lookup: False})


class AnswerFilterSet(FilterSet):
    created_at = DateTimeFromToRangeFilter()
    problem = NumberFilter(method='filter_problem')
    team = ModelChoiceFilter(queryset=Team.objects.all(), method='filter_team')

    def filter_problem(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(smallanswer__problem__id=value) | Q(biganswer__problem__id=value) | Q(
                multichoiceanswer__problem__id=value) | Q(uploadfileanswer__problem__id=value))
        return queryset

    class Meta:
        model = Answer
        fields = ['problem', 'is_final_answer', 'created_at', 'answer_type']


class TeamFilterSet(FilterSet):

    class Meta:
        model = Team
        fields = ['registration_form']
