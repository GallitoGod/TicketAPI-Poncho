from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .router import router
from django.views.static import serve # Esto sirve imagenes directamente
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('index/', include(router.urls)),
    path('', TemplateView.as_view(template_name= 'ERS.html'), name= 'ers_doc'),
    path('images/<path:path>', serve, {'document_root': 'templates/images/'}),
    #   Basicamente esto hace una vista generica porque django solo procesa urls como funciones
    # y ahi le estoy pasando un html que en caso de hacer la peticion GET, TemplateView va a generar un HttpResponse 
    # mandandome el HTML directamente sin tener que agregarlo a un script view, deja el codigo mas limpio vaya.

    # Endpoints de SimpleJWT para login
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api-auth/', include('rest_framework.urls')), # Para poder loguear un usuario mediante la interfaz de Browsable API
]
