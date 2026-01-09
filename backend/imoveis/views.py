from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Q
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Imovel
from .serializers import ImovelSerializer

# =========================
# FRONTEND (HTML)
# =========================
def index(request):
    imoveis = Imovel.objects.filter(ativo=True).annotate(
        menor_preco=Min('unidades__preco'),
        min_quartos=Min('unidades__quartos'),
        max_quartos=Max('unidades__quartos'), 
        min_area=Min('unidades__area_m2'),
        max_area=Max('unidades__area_m2')     
    ).prefetch_related('imagens', 'unidades')

    bairro = request.GET.get('bairro')
    tipo = request.GET.get('tipo')
    quartos = request.GET.get('quartos')

    if bairro:
        imoveis = imoveis.filter(bairro__icontains=bairro)

    if tipo:
        imoveis = imoveis.filter(tipo=tipo)

    if quartos:
        imoveis = imoveis.filter(quartos__gte=quartos)

    context = {
        'imoveis': imoveis,
        'bairro_selecionado': bairro,
        'tipo_selecionado': tipo,
        'quartos_selecionados': quartos,
    }

    return render(request, 'imoveis/index.html', context)

def imovel_detalhe(request, slug):
# Adicionamos 'unidades__imagens' para trazer as fotos de cada planta
    imovel = get_object_or_404(
        Imovel.objects.prefetch_related('unidades__imagens', 'imagens'), 
        slug=slug, 
        ativo=True
    )

    mensagem = (
        f"Olá! Tenho interesse no imóvel "
        f"{imovel.titulo} - {imovel.bairro}. "
        f"Link: {request.build_absolute_uri()}"
    )

    whatsapp_url = (
        f"https://wa.me/{settings.WHATSAPP_NUMERO}"
        f"?text={mensagem.replace(' ', '%20')}"
    )
    return render(request, 'imoveis/detalhe.html', {'imovel': imovel, "whatsapp_url": whatsapp_url})

# =========================
# API (JSON)
# =========================
class ImovelListAPIView(ListAPIView):
    queryset = Imovel.objects.filter(ativo=True)
    serializer_class = ImovelSerializer


class ImovelDetailAPIView(RetrieveAPIView):
    queryset = Imovel.objects.filter(ativo=True)
    serializer_class = ImovelSerializer
