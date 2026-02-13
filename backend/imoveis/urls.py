# backend/imoveis/urls.py
from django.urls import path
from .views import (
    buscar_unidades_ajax,
    imovel_detalhe,
    index,
    sobre_nos,
    termos_de_uso,
    politica_de_privacidade,
    # blog,
    duvidas_frequentes,
    simulacao_financiamento,
    simulacao_mcmv,
    pagina_mcmv,
    fale_conosco,
    ImovelListAPIView,
    ImovelDetailAPIView,
    custom_admin_index,
    custom_admin_imoveis_list,
    custom_admin_delete_imovel,
    custom_admin_imovel_imagens,
    custom_admin_delete_imagem,
    custom_admin_imovel_arquivos,
    custom_admin_delete_arquivo,
    custom_admin_imovel_unidades,
    custom_admin_criar_unidade,
    custom_admin_delete_unidade,
    custom_admin_imovel_instalacoes,
    custom_admin_criar_instalacao,
    custom_admin_criar_imovel,
    custom_admin_editar_imovel,
    custom_admin_editar_unidade,
    custom_admin_importar_orulo, # Importação
    custom_admin_orulo_list, # Lista Órulo
    custom_admin_sync_orulo_imovel, # Sync Unitário
    check_import_progress, # Ajax Progresso
    custom_admin_exportar_imoveis, # Exportar Excel
)

app_name = 'imoveis'

urlpatterns = [
    path('gerenciador/orulo/', custom_admin_orulo_list, name='custom_admin_orulo_list'),
    path('gerenciador/orulo/sync/<int:imovel_id>/', custom_admin_sync_orulo_imovel, name='custom_admin_sync_orulo_imovel'),
    path('gerenciador/orulo/progress/', check_import_progress, name='check_import_progress'),
    path('gerenciador/imoveis/exportar/', custom_admin_exportar_imoveis, name='custom_admin_exportar_imoveis'), # Novo endpoint

    # ======================
    # FRONTEND (HTML)
    # ======================
    path('', index, name='home'),
    path('sobre-nos/', sobre_nos, name='sobre_nos'),
    path('termos-de-uso/', termos_de_uso, name='termos_de_uso'),
    path('politica-de-privacidade/', politica_de_privacidade, name='politica_de_privacidade'),
    # path('blog/', blog, name='blog'), # Removido, agora no app blog
    # path('duvidas-frequentes/', duvidas_frequentes, name='duvidas_frequentes'),
    path('simulacao/financiamento/', simulacao_financiamento, name='simulacao_financiamento'),
    path('simulacao/minha-casa-minha-vida/', simulacao_mcmv, name='simulacao_mcmv'),
    path('minha-casa-minha-vida/', pagina_mcmv, name='pagina_mcmv'),
    path('fale-conosco/', fale_conosco, name='fale_conosco'),

    # ======================
    # CUSTOM ADMIN
    # ======================
    path('gerenciador/', custom_admin_index, name='custom_admin_index'),
    path('gerenciador/importar-orulo/', custom_admin_importar_orulo, name='custom_admin_importar_orulo'),  # Nova rota
    path('gerenciador/imoveis/', custom_admin_imoveis_list, name='custom_admin_imoveis_list'),
    path('gerenciador/novo/', custom_admin_criar_imovel, name='custom_admin_criar_imovel'),
    path('gerenciador/editar/<int:imovel_id>/', custom_admin_editar_imovel, name='custom_admin_editar_imovel'),
    path('gerenciador/imovel/<int:imovel_id>/imagens/', custom_admin_imovel_imagens, name='custom_admin_imovel_imagens'),    path('gerenciador/imoveis/<int:imovel_id>/delete/', custom_admin_delete_imovel, name='custom_admin_delete_imovel'),    path('gerenciador/imagem/<int:imagem_id>/delete/', custom_admin_delete_imagem, name='custom_admin_delete_imagem'),
    
    path('gerenciador/imovel/<int:imovel_id>/arquivos/', custom_admin_imovel_arquivos, name='custom_admin_imovel_arquivos'),
    path('gerenciador/arquivo/<int:arquivo_id>/delete/', custom_admin_delete_arquivo, name='custom_admin_delete_arquivo'),

    path('gerenciador/imovel/<int:imovel_id>/unidades/', custom_admin_imovel_unidades, name='custom_admin_imovel_unidades'),
    path('gerenciador/imovel/<int:imovel_id>/unidades/nova/', custom_admin_criar_unidade, name='custom_admin_criar_unidade'),
    path('gerenciador/unidade/<int:unidade_id>/editar/', custom_admin_editar_unidade, name='custom_admin_editar_unidade'),
    path('gerenciador/unidade/<int:unidade_id>/delete/', custom_admin_delete_unidade, name='custom_admin_delete_unidade'),

    path('gerenciador/imovel/<int:imovel_id>/instalacoes/', custom_admin_imovel_instalacoes, name='custom_admin_imovel_instalacoes'),
    path('gerenciador/instalacoes/nova/', custom_admin_criar_instalacao, name='custom_admin_criar_instalacao'),

    # ======================
    # API (JSON)
    # ======================
    path('api/imoveis/', ImovelListAPIView.as_view(), name='api-imoveis-list'),
    path('api/imoveis/<int:pk>/', ImovelDetailAPIView.as_view(), name='api-imoveis-detail'),
    path('imovel/<slug:slug>/', imovel_detalhe, name='imovel_detalhe'),
    path('ajax/buscar-unidades/', buscar_unidades_ajax, name='ajax_buscar_unidades'),
]
