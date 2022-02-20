from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet


def paginator_page(queryset: QuerySet, page: int, showing_posts: int) -> Page:
    paginator = Paginator(queryset, showing_posts)
    return paginator.get_page(page)
