from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


class PaginatorMixin(object):
    def __init__(self, queryset, request_page):
        self.queryset = queryset
        self.request_page = request_page

    def queryset_paginated(self):
        paginator = Paginator(self.queryset, settings.SHOWING_POSTS)
        try:
            queryset_paginated = paginator.page(self.request_page)
        except PageNotAnInteger:
            queryset_paginated = paginator.page(1)
        except EmptyPage:
            queryset_paginated = paginator.page(paginator.num_pages)

        return queryset_paginated
