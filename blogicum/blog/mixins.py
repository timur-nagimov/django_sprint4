from .models import Post
from .constants import MAIN_PAGE_MAX_POSTS


class PaginatorListMixin:
    model = Post
    paginate_by = MAIN_PAGE_MAX_POSTS
