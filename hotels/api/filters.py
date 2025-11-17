from django_filters import rest_framework as filters
from ..models import Hotel


class HotelFilter(filters.FilterSet):
    """Фильтры для списка отелей"""
    
    # Точное совпадение
    country = filters.NumberFilter(field_name='country_id')
    city = filters.NumberFilter(field_name='city_id')
    stars = filters.NumberFilter(field_name='stars')
    
    # Диапазон цен
    min_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    
    # Поиск по названию и описанию
    search = filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        """Поиск по названию, описанию и городу"""
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(city__name__icontains=value)
        )
    
    class Meta:
        model = Hotel
        fields = ['country', 'city', 'stars', 'min_price', 'max_price', 'search']

