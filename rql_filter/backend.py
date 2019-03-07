from django.conf import settings
from rest_framework.filters import BaseFilterBackend

from rql_filter.parser import create_django_orm_condition, parse_rql


class RQLFilterBackend(BaseFilterBackend):
    """
    Filter that uses a RQL query.

    The RQL query is expected to be passed as a querystring parameter.
    The RQL_FILTER_QUERY_PARAM setting (which defaults to 'q') specifies the
    name of the querystring parameter used.
    """

    query_param = getattr(settings, 'RQL_FILTER_QUERY_PARAM', 'q')

    def filter_queryset(self, request, queryset, view):
        qs = queryset

        if self.query_param in request.GET:
            if len(request.GET[self.query_param]):

                condition = create_django_orm_condition(
                    parse_rql(request.GET[self.query_param])
                )

                qs = qs.filter(condition)

        return qs
