import django_filters
from .models import *

class DesignerWorkFilter(django_filters.FilterSet):
    hashtag = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ChoiceFilter(field_name='category__name', choices=Category.objects.all().values_list('name', 'name').distinct())

    class Meta:
        model = DesignerWork
        fields = ['hashtag', 'category']
