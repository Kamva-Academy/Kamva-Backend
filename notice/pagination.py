from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from .exception import NoResult

DEFAULT_PAGE_SIZE = 8


def pagination_result(data, page_number=1, page_size=DEFAULT_PAGE_SIZE):
    if page_number == "0":
        page_number = 1
    result = dict()
    p = Paginator(data, page_size)
    try:
        page = p.page(page_number)
    except EmptyPage:
        raise NoResult()
    result['result'] = page.object_list
    result['has_next'] = page.has_next()
    result['has_previous'] = page.has_previous()
    result['all_page'] = p.num_pages
    result['count'] = p.count

    page = str(p.page(page_number)).replace("<Page ", "").replace(">", "")
    result['page'] = page
    return result
