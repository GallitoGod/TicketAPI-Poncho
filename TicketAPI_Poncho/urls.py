"""
URL configuration for TicketAPI_Poncho project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .router import router
from django.views.static import serve # Esto sirve imagenes directamente

urlpatterns = [
    path("admin/", admin.site.urls),
    path('index/', include(router.urls)),
    path('', TemplateView.as_view(template_name= 'ERS.html'), name= 'ers_doc'),
    path('images/<path:path>', serve, {'document_root': 'templates/images/'}),
    #   Basicamente esto hace una vista generica porque django solo procesa urls como funciones
    # y ahi le estoy pasando un html que en caso de hacer la peticion GET, TemplateView va a generar un HttpResponse 
    # mandandome el HTML directamente sin tener que agregarlo a un script view, deja el codigo mas limpio vaya.
]
