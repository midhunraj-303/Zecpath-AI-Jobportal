
"""
Reusable pagination classes for the Zecpath ATS API.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Provide configurable page-number pagination.

    Default page size: 10 records.
    Maximum page size: 100 records.
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
