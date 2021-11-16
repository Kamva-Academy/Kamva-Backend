from django.db.models import Q
from django_filters.rest_framework import FilterSet, ModelMultipleChoiceFilter, DateTimeFromToRangeFilter, \
    ModelChoiceFilter, NumberFilter, UUIDFilter
from django_filters.widgets import CSVWidget

from fsm.models import Answer, Problem, Team


class AnswerFilterSet(FilterSet):
    created_at = DateTimeFromToRangeFilter()
    problem = NumberFilter(method='filter_problem')
    team = ModelChoiceFilter(queryset=Team.objects.all(), method='filter_team')

    class Meta:
        model = Answer
        fields = ['problem', 'is_final_answer', 'created_at', 'answer_type']

    def filter_problem(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(smallanswer__problem__id=value) | Q(biganswer__problem__id=value) | Q(
                multichoiceanswer__problem__id=value) | Q(uploadfileanswer__problem__id=value))
        return queryset
