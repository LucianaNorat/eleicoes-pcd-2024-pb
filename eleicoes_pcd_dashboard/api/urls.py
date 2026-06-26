from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("subnotificacao/", views.subnotificacao, name="subnotificacao"),
    path("distribuicao-zona/", views.distribuicao_zona, name="distribuicao_zona"),
    path("abstencao-vs-pcd/", views.abstencao_vs_pcd, name="abstencao_vs_pcd"),
    path("pcd-obrigatorio/", views.pcd_obrigatorio, name="pcd_obrigatorio"),
    path("perfil-demografico/", views.perfil_demografico, name="perfil_demografico"),
    path("locais-votacao/", views.locais_votacao, name="locais_votacao"),
    path("porte-municipio/",  views.porte_municipio, name="porte_municipio"),
    path("zonas-por-municipio/", views.zonas_por_municipio, name="zonas_por_municipio"),
]