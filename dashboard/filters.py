import django_filters
from django.db.models import Q
from .models import Data

class DataFilter(django_filters.FilterSet):
    # Time-Based Filters
    added = django_filters.DateFromToRangeFilter()
    published = django_filters.DateFromToRangeFilter()
    start_year = django_filters.CharFilter(lookup_expr='exact')
    end_year = django_filters.CharFilter(lookup_expr='exact')

    # Numerical Filters (Now Range-Based)
    intensity = django_filters.RangeFilter()
    relevance = django_filters.RangeFilter()
    likelihood = django_filters.RangeFilter()
    impact = django_filters.RangeFilter()

    # Categorical & Text Filters
    sector = django_filters.CharFilter(lookup_expr='icontains')
    topic = django_filters.CharFilter(lookup_expr='icontains')
    region = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    pestle = django_filters.CharFilter(lookup_expr='icontains')
    source = django_filters.CharFilter(lookup_expr='icontains')

    # SWOT Filter (Derived from PESTLE)
    swot = django_filters.CharFilter(method='filter_swot')
    title_insight = django_filters.CharFilter(method='filter_title_insight')

    SWOT_MAPPING = {
        "strength": "Economic",
        "weakness": "Social",
        "opportunity": "Technological",
        "threat": "Political"
    }

    def filter_swot(self, queryset, name, value):
        mapped_pestle = self.SWOT_MAPPING.get(value.lower())
        if mapped_pestle:
            return queryset.filter(pestle__icontains=mapped_pestle)
        return queryset

    def filter_title_insight(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(insight__icontains=value))

    class Meta:
        model = Data
        fields = [
            'end_year', 'start_year', 'added', 'published',
            'intensity', 'relevance', 'likelihood', 'impact',
            'sector', 'topic', 'region', 'country', 'city', 'pestle', 'source',
            'swot', 'title_insight'
        ]