import django_filters
from users.models import User


class UserFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', lookup_expr='exact')
    email = django_filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = User
        fields = []