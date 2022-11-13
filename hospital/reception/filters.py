import django_filters
from django import forms
from datetime import datetime, timedelta, timezone

from reception.models import Ticket


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


class TicketFilter(django_filters.FilterSet):

    def only_accessible(self):
        days = 30
        amount_of_receipts = 20

        now = datetime.now().replace(second=0, microsecond=0, tzinfo=timezone.utc)
        if now.hour >= 19: now.replace(day=now.day + 1, hour=12, minute=0)
        now += timedelta(minutes=(30 - now.minute % 30))
        tickets_times = [now + timedelta(minutes=30 * minutes_step, days=day_step)
                         for minutes_step in
                         range(amount_of_receipts) for day_step in range(days) if
                         (now + timedelta(minutes=30 * minutes_step, days=day_step)).hour < 19]

        tickets_data = self.qs.filter(
            receipt_time__date__gte=datetime.now(),
        ).values('receipt_time', 'id')

        tickets_receipt_time = [receipt_data_item['receipt_time'] for receipt_data_item in tickets_data]

        accessible_dates = sorted(set(tickets_times) - set(tickets_receipt_time))

        return accessible_dates
