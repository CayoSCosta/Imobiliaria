# backend/imoveis/urls.py
from django.urls import path
from .views import (
    imovel_detalhe,
    index,
    ImovelListAPIView,
    ImovelDetailAPIView,
)

urlpatterns = [
    # ======================
    # FRONTEND (HTML)
    # ======================
    path('', index, name='home'),

    # ======================
    # API (JSON)
    # ======================
    path('api/imoveis/', ImovelListAPIView.as_view(), name='api-imoveis-list'),
    path('api/imoveis/<int:pk>/', ImovelDetailAPIView.as_view(), name='api-imoveis-detail'),
    path('imovel/<slug:slug>/', imovel_detalhe, name='imovel_detalhe'),
]
