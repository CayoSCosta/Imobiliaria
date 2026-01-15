from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Min, Max, Q
from django.conf import settings
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Imovel, Unidade, ImagemImovel, Instalacao, ImagemUnidade
from .serializers import ImovelSerializer
from django.http import JsonResponse
from .forms import (
    ImovelImagensForm, 
    UnidadeForm, 
    ImovelInstalacoesForm, 
    ImovelForm,
    InstalacaoForm
)

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

def buscar_unidades_ajax(request):
    imovel_id = request.GET.get('imovel_id')
    unidades = Unidade.objects.filter(imovel_id=imovel_id).values('id', 'titulo')
    return JsonResponse(list(unidades), safe=False)

# =========================
# CUSTOM ADMIN
# =========================
def custom_admin_index(request):
    """Dashboard principal que permite escolher entre Imóveis e Leads"""
    return render(request, 'custom_admin/dashboard.html')

def custom_admin_imoveis_list(request):
    imoveis = Imovel.objects.all().order_by('-criado_em')
    return render(request, 'custom_admin/imoveis_list.html', {'imoveis': imoveis})

def custom_admin_imovel_imagens(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            form = ImovelImagensForm(request.POST, request.FILES)
            if form.is_valid():
                imagens = request.FILES.getlist('imagens')
                for imagem in imagens:
                    ImagemImovel.objects.create(imovel=imovel, imagem=imagem)
                return redirect('custom_admin_imovel_imagens', imovel_id=imovel.id)
        
        elif action == 'update_order':
            imagem_principal_id = request.POST.get('principal')
            
            # Se foi selecionada uma imagem principal, reseta as outras
            if imagem_principal_id:
                imovel.imagens.update(principal=False)

            # Atualiza ordem e principal de cada imagem
            for key, value in request.POST.items():
                if key.startswith('ordem_'):
                    try:
                        imagem_id = int(key.split('_')[1])
                        ordem = int(value)
                        
                        imagem = ImagemImovel.objects.get(pk=imagem_id, imovel=imovel)
                        imagem.ordem = ordem
                        
                        if str(imagem.id) == imagem_principal_id:
                            imagem.principal = True
                        
                        imagem.save()
                    except (ValueError, ImagemImovel.DoesNotExist):
                        continue
            
            return redirect('custom_admin_imovel_imagens', imovel_id=imovel.id)

    else:
        form = ImovelImagensForm()
    
    imagens_existentes = imovel.imagens.all()
    return render(request, 'custom_admin/imovel_imagens.html', {
        'imovel': imovel,
        'form': form,
        'imagens': imagens_existentes
    })

def custom_admin_delete_imagem(request, imagem_id):
    imagem = get_object_or_404(ImagemImovel, pk=imagem_id)
    imovel_id = imagem.imovel.id
    imagem.delete()
    return redirect('custom_admin_imovel_imagens', imovel_id=imovel_id)

def custom_admin_imovel_unidades(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    unidades = imovel.unidades.all()
    return render(request, 'custom_admin/imovel_unidades.html', {'imovel': imovel, 'unidades': unidades})

def custom_admin_criar_unidade(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    if request.method == 'POST':
        form = UnidadeForm(request.POST, request.FILES)
        if form.is_valid():
            unidade = form.save(commit=False)
            unidade.imovel = imovel
            unidade.save()

            if request.FILES.get('imagem_planta'):
                ImagemUnidade.objects.create(
                    unidade=unidade, 
                    imagem=request.FILES['imagem_planta'],
                    principal=True
                )

            return redirect('custom_admin_imovel_unidades', imovel_id=imovel.id)
    else:
        form = UnidadeForm()
    return render(request, 'custom_admin/criar_unidade.html', {'imovel': imovel, 'form': form, 'titulo': 'Nova Unidade'})

def custom_admin_editar_unidade(request, unidade_id):
    unidade = get_object_or_404(Unidade, pk=unidade_id)
    imovel = unidade.imovel
    
    if request.method == 'POST':
        form = UnidadeForm(request.POST, request.FILES, instance=unidade)
        if form.is_valid():
            unidade = form.save()

            if request.FILES.get('imagem_planta'):
                # Opcional: Limpar anteriores se quiser só uma planta por unidade
                # unidade.imagens.all().delete()
                ImagemUnidade.objects.create(
                    unidade=unidade, 
                    imagem=request.FILES['imagem_planta'],
                    principal=True
                )
            
            return redirect('custom_admin_imovel_unidades', imovel_id=imovel.id)
    else:
        form = UnidadeForm(instance=unidade)
    
    return render(request, 'custom_admin/criar_unidade.html', {
        'imovel': imovel, 
        'form': form, 
        'titulo': f'Editar {unidade.titulo}'
    })

def custom_admin_delete_unidade(request, unidade_id):
    unidade = get_object_or_404(Unidade, pk=unidade_id)
    imovel_id = unidade.imovel.id
    unidade.delete()
    return redirect('custom_admin_imovel_unidades', imovel_id=imovel_id)

def custom_admin_imovel_instalacoes(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    if request.method == 'POST':
        form = ImovelInstalacoesForm(request.POST, instance=imovel)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_imovel_instalacoes', imovel_id=imovel.id)
    else:
        form = ImovelInstalacoesForm(instance=imovel)
    
    instalacao_form = InstalacaoForm()
    
    return render(request, 'custom_admin/imovel_instalacoes.html', {
        'imovel': imovel,
        'form': form,
        'instalacao_form': instalacao_form
    })

def custom_admin_criar_instalacao(request):
    if request.method == 'POST':
        form = InstalacaoForm(request.POST)
        if form.is_valid():
            form.save()
            # Retorna para a página anterior ou para admin index se não houver referer
            next_url = request.META.get('HTTP_REFERER', 'custom_admin_imoveis_list')
            return redirect(next_url)
    return redirect('custom_admin_imoveis_list')

def custom_admin_criar_imovel(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST)
        if form.is_valid():
            imovel = form.save()
            # Redireciona para a edição de imagens ou lista, vamos para imagens para incentivar o cadastro completo
            return redirect('custom_admin_imovel_imagens', imovel_id=imovel.id)
    else:
        form = ImovelForm()
    return render(request, 'custom_admin/criar_imovel.html', {'form': form})

def custom_admin_editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    if request.method == 'POST':
        form = ImovelForm(request.POST, instance=imovel)
        if form.is_valid():
            imovel = form.save()
            return redirect('custom_admin_imoveis_list')
    else:
        form = ImovelForm(instance=imovel)
    return render(request, 'custom_admin/criar_imovel.html', {'form': form, 'imovel': imovel})