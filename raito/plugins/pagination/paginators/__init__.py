from .base import BasePaginator
from .inline import InlinePaginator
from .list import ListPaginator
from .photo import PhotoPaginator
from .protocol import IPaginator
from .text import TextPaginator

__all__ = (
    "BasePaginator",
    "IPaginator",
    "InlinePaginator",
    "ListPaginator",
    "PhotoPaginator",
    "TextPaginator",
)
