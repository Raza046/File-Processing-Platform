from rest_framework.pagination import PageNumberPagination


class FileListPagination(PageNumberPagination):

    page_size = 10
    page_query_param = "page_size"
    max_page_size = 100


class ProcesingHistoryPagination(PageNumberPagination):

    page_size = 10
    page_query_param = "page_size"
    max_page_size = 100


