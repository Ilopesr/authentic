from authentic.conf import settings
from rest_framework.pagination import LimitOffsetPagination


class AuthenticPagination(LimitOffsetPagination):
    default_limit = settings.PAGE_SIZE if settings.PAGE_SIZE >= 1 else 1
    max_limit = 100
