from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10 # Cantidad de elementos por página por defecto
    page_query_param = 'page' 
    page_size_query_param = 'page_size' 
    max_page_size = 20 # Límite de seguridad para evitar que pidan 1 millón de registros de golpe