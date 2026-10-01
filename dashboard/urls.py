from django.urls import path

from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('exportar/citas.xml', views.exportar_citas_xml, name='exportar_citas_xml'),
]
