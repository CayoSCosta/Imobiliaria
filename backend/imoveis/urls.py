# backend/imoveis/urls.py
from django.urls import path
from .views import (
    buscar_unidades_ajax,
    imovel_detalhe,
    index,
    ImovelListAPIView,
    ImovelDetailAPIView,
    custom_admin_index,
    custom_admin_imoveis_list,
    custom_admin_imovel_imagens,
    custom_admin_delete_imagem,
    custom_admin_imovel_unidades,
    custom_admin_criar_unidade,
    custom_admin_delete_unidade,
    custom_admin_imovel_instalacoes,
    custom_admin_criar_instalacao,
    custom_admin_criar_imovel,
    custom_admin_editar_imovel,
    custom_admin_editar_unidade,
)

urlpatterns = [
    # ======================
    # FRONTEND (HTML)
    # ======================
    path('', index, name='home'),

    # ======================
    # CUSTOM ADMIN
    # ======================
    path('custom-admin/', custom_admin_index, name='custom_admin_index'),
    path('custom-admin/imoveis/', custom_admin_imoveis_list, name='custom_admin_imoveis_list'),
    path('custom-admin/novo/', custom_admin_criar_imovel, name='custom_admin_criar_imovel'),
    path('custom-admin/editar/<int:imovel_id>/', custom_admin_editar_imovel, name='custom_admin_editar_imovel'),
    path('custom-admin/imovel/<int:imovel_id>/imagens/', custom_admin_imovel_imagens, name='custom_admin_imovel_imagens'),
    path('custom-admin/imagem/<int:imagem_id>/delete/', custom_admin_delete_imagem, name='custom_admin_delete_imagem'),
    
    path('custom-admin/imovel/<int:imovel_id>/unidades/', custom_admin_imovel_unidades, name='custom_admin_imovel_unidades'),
    path('custom-admin/imovel/<int:imovel_id>/unidades/nova/', custom_admin_criar_unidade, name='custom_admin_criar_unidade'),
    path('custom-admin/unidade/<int:unidade_id>/editar/', custom_admin_editar_unidade, name='custom_admin_editar_unidade'),
    path('custom-admin/unidade/<int:unidade_id>/delete/', custom_admin_delete_unidade, name='custom_admin_delete_unidade'),

    path('custom-admin/imovel/<int:imovel_id>/instalacoes/', custom_admin_imovel_instalacoes, name='custom_admin_imovel_instalacoes'),
    path('custom-admin/instalacoes/nova/', custom_admin_criar_instalacao, name='custom_admin_criar_instalacao'),

    # ======================
    # API (JSON)
    # ======================
    path('api/imoveis/', ImovelListAPIView.as_view(), name='api-imoveis-list'),
    path('api/imoveis/<int:pk>/', ImovelDetailAPIView.as_view(), name='api-imoveis-detail'),
    path('imovel/<slug:slug>/', imovel_detalhe, name='imovel_detalhe'),
    path('ajax/buscar-unidades/', buscar_unidades_ajax, name='ajax_buscar_unidades'),
]
