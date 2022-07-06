from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # if we cannot get page number from url, it will be set 20 as default
    page_size = 20
    # the default value for page_size_query_param is None
    # which means users are not allowed to specify the size of page
    # here we set the size to to specify one based on different type of devices
    page_size_query_param = 'size'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })
