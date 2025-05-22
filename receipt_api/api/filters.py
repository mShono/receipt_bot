import django_filters

from .models import (ExpenseItem)


class ExpenseItemFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='product__category', lookup_expr='exact')
    chat_id  = django_filters.NumberFilter(field_name='expense__user__chat_id', lookup_expr='exact')
    created_at__range = django_filters.CharFilter(method='filter_created_at_range')

    def filter_created_at_range(self, queryset, name, value):
        try:
            start, end = value.split(',')
            return queryset.filter(expense__created_at__range=[start, end])
        except ValueError:
            return queryset.none()

    class Meta:
        model = ExpenseItem
        fields = ['chat_id', 'category', 'created_at__range']