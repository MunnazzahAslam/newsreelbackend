from django_filters import rest_framework as filters

from posts.models import Post


class PostFilter(filters.FilterSet):
    exclude = filters.CharFilter(method='exclude_post_types')

    class Meta:
        model = Post
        fields = ('type', 'exclude')

    def exclude_post_types(self, queryset, name, value):
        types = value.split(',')
        queryset = queryset.exclude(type__in=types)
        return queryset
