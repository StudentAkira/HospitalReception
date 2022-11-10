import django_filters
from django import forms


class PatientFilter(django_filters.FilterSet):

    appointed_only = django_filters.BooleanFilter(
        field_name='ticket_owner',
        method='filter_appointed',
        label='Only appointed : ',
        widget=forms.CheckboxInput,
    )

    def filter_appointed(self, queryset, name, value):
        if value:
            queryset = queryset.filter(ticket_owner__target=self.request.user)
        return queryset
