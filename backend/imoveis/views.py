from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Min, Max, Q, F, Value, FloatField
from django.db.models.functions import ACos, Cos, Radians, Sin, Cast
from django.conf import settings
from django.utils.text import slugify
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Imovel, Unidade, ImagemImovel, Instalacao, ImagemUnidade, ArquivoImovel
from .serializers import ImovelSerializer
from django.http import JsonResponse
from leads.models import Lead
from .forms import (
    ImovelImagensForm, 
    UnidadeForm, 
    ImovelInstalacoesForm, 
    ImovelForm,
    InstalacaoForm,
    ImovelArquivosForm
)

# =========================
# FRONTEND (HTML)
# =========================
from django.core.paginator import Paginator

def index(request):
    imoveis = Imovel.objects.filter(ativo=True).annotate(
        menor_preco=Min('unidades__preco'),
        min_quartos=Min('unidades__quartos'),
        max_quartos=Max('unidades__quartos'), 
        min_area=Min('unidades__area_m2'),
        max_area=Max('unidades__area_m2')     
    ).prefetch_related('imagens', 'unidades')

    # Destaques para o Hero (Carrossel)
    destaques = imoveis.filter(destaque=True)[:5] # Pegar os 5 primeiros destaques

    # Filtros
    termo = request.GET.get('termo')
    tipo = request.GET.get('tipo')
    status = request.GET.get('status')
    quartos = request.GET.get('quartos')
    vagas = request.GET.get('vagas')
    banheiros = request.GET.get('banheiros')
    suites = request.GET.get('suites')
    area_min = request.GET.get('area_min')
    area_max = request.GET.get('area_max')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    
    # Geolocalização
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if lat and lng:
        try:
            user_lat = float(lat)
            user_lon = float(lng)
            
            # Filtra apenas imóveis com coordenadas
            imoveis = imoveis.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
            
            # Constantes para fórmula (convertendo input para radianos diretamente no python ou db)
            # Para evitar erros de banco, usamos functions do Django
            # Fórmula Haversine: 6371 * acos(cos(rad(user_lat)) * cos(rad(lat)) * cos(rad(long) - rad(user_lon)) + sin(rad(user_lat)) * sin(rad(lat)))
            
            # Nota: Isso requer suporte do banco de dados para funções trigonométricas. Postgres tem.
            
            imoveis = imoveis.annotate(
                distance=6371 * ACos(
                    Cos(Radians(user_lat)) * 
                    Cos(Radians(Cast(F('latitude'), FloatField()))) * 
                    Cos(Radians(Cast(F('longitude'), FloatField())) - Radians(user_lon)) + 
                    Sin(Radians(user_lat)) * 
                    Sin(Radians(Cast(F('latitude'), FloatField())))
                )
            ).order_by('distance')
            
        except ValueError:
            pass # Ignora se lat/lng inválidos

    if termo:
        imoveis = imoveis.filter(Q(bairro__icontains=termo) | Q(titulo__icontains=termo))

    if tipo:
        imoveis = imoveis.filter(tipo=tipo)

    if status:
        imoveis = imoveis.filter(status=status)

    if quartos:
        imoveis = imoveis.filter(unidades__quartos__gte=quartos).distinct()

    if vagas:
        imoveis = imoveis.filter(unidades__vagas__gte=vagas).distinct()
    
    if banheiros:
        imoveis = imoveis.filter(unidades__banheiros__gte=banheiros).distinct()

    if suites:
        imoveis = imoveis.filter(unidades__suites__gte=suites).distinct()

    if area_min:
        imoveis = imoveis.filter(unidades__area_m2__gte=area_min).distinct()

    if area_max:
        imoveis = imoveis.filter(unidades__area_m2__lte=area_max).distinct()

    if preco_min:
        imoveis = imoveis.filter(unidades__preco__gte=preco_min).distinct()

    if preco_max:
        imoveis = imoveis.filter(unidades__preco__lte=preco_max).distinct()

    # Paginação
    paginator = Paginator(imoveis, 9) # 9 imóveis por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'imoveis': page_obj, 
        'destaques': destaques,
        'termo_selecionado': termo,
        'tipo_selecionado': tipo,
        'status_selecionado': status,
        'quartos_selecionados': quartos,
        'vagas_selecionadas': vagas,
        'banheiros_selecionados': banheiros,
        'suites_selecionadas': suites,
        'area_min_selecionada': area_min,
        'area_max_selecionada': area_max,
        'preco_min_selecionado': preco_min,
        'preco_max_selecionado': preco_max,
    }

    return render(request, 'imoveis/index.html', context)

def sobre_nos(request):
    return render(request, 'institucional/sobre_nos.html')

def termos_de_uso(request):
    return render(request, 'termos_de_uso.html')

def politica_de_privacidade(request):
    return render(request, 'politica_de_privacidade.html')

# def blog(request):
#    return render(request, 'institucional/blog.html')

def duvidas_frequentes(request):
    return render(request, 'institucional/duvidas_frequentes.html')

def simulacao_financiamento(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        nome = data.get('nome')
        telefone = data.get('telefone')
        email = data.get('email')
        
        conteudo = f"Origem: Simulador de Financiamento\nE-mail: {email}"
        
        Lead.objects.create(
            nome=nome,
            telefone=telefone,
            mensagem=conteudo,
            status='novo'
        )
        return JsonResponse({'success': True})

    return render(request, 'simuladores/financiamento.html')

def simulacao_mcmv(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        nome = data.get('nome')
        telefone = data.get('telefone')
        email = data.get('email')
        
        conteudo = f"Origem: Simulador Minha Casa Minha Vida\nE-mail: {email}"
        
        Lead.objects.create(
            nome=nome,
            telefone=telefone,
            mensagem=conteudo,
            status='novo'
        )
        return JsonResponse({'success': True})

    return render(request, 'simuladores/mcmv.html')

def fale_conosco(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')

        # Constrói uma mensagem composta já que o modelo de Lead (ainda) não tem campo e-mail separado
        conteudo_completo = f"Origem: Fale Conosco\nAssunto: {assunto}\nE-mail: {email}\n\nMensagem:\n{mensagem}"

        Lead.objects.create(
            nome=nome,
            telefone=telefone,
            mensagem=conteudo_completo,
            tipo_contato='whatsapp', # Padrão
            status='novo'
        )

        return render(request, 'institucional/fale_conosco.html', {'sucesso': True})
    return render(request, 'institucional/fale_conosco.html')

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
@staff_member_required
def custom_admin_index(request):
    """Dashboard principal que permite escolher entre Imóveis e Leads"""
    return render(request, 'custom_admin/dashboard.html')

@staff_member_required
def custom_admin_imoveis_list(request):
    imoveis_list = Imovel.objects.all().order_by('-criado_em')

    # Filtros
    titulo = request.GET.get('titulo')
    bairro = request.GET.get('bairro')
    status = request.GET.get('status')

    if titulo:
        imoveis_list = imoveis_list.filter(Q(titulo__icontains=titulo) | Q(slug__icontains=slugify(titulo)))
    
    if bairro:
        imoveis_list = imoveis_list.filter(Q(bairro__icontains=bairro) | Q(slug__icontains=slugify(bairro)))

    if status:
        imoveis_list = imoveis_list.filter(status=status)
    
    paginator = Paginator(imoveis_list, 10)  # Mostra 10 imóveis por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'imoveis': page_obj, 
        'page_obj': page_obj,
        'titulo_filtro': titulo,
        'bairro_filtro': bairro,
        'status_filtro': status,
        'status_choices': Imovel.STATUS_CHOICES,
    }

    return render(request, 'custom_admin/imoveis_list.html', context)
@staff_member_required
def custom_admin_delete_imovel(request, imovel_id):
    """Exclui um imóvel específico"""
    imovel = get_object_or_404(Imovel, id=imovel_id)
    if request.method == 'POST':
        imovel.delete()
        # messages.success(request, f'Imóvel "{imovel.titulo}" excluído com sucesso!') # Se tiver messages
        return redirect('custom_admin_imoveis_list')
    
    # Se for GET, não faz nada ou renderiza confirmação (mas vamos usar modal e POST)
    return redirect('custom_admin_imoveis_list')

@staff_member_required
def custom_admin_sync_orulo_imovel(request, imovel_id):
    """View para sincronizar um imóvel específico"""
    sucesso, resultado = sincronizar_imovel_orulo(imovel_id)
    
    # Se for requisição AJAX, retorna JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': sucesso,
            'message': resultado['message'],
            'changes': resultado['changes'],
            'removed': resultado['removed']
        })

    # Fallback para redirect normal
    if sucesso:
        messages.success(request, resultado['message'])
    else:
        messages.error(request, resultado['message'])
        
    return redirect('custom_admin_orulo_list')
@staff_member_required
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
            
        elif action == 'move_to_unit':
            imagem_id = request.POST.get('imagem_id')
            unidade_id = request.POST.get('unidade_id')
            
            try:
                from django.core.files.base import ContentFile
                
                img_imovel = ImagemImovel.objects.get(pk=imagem_id, imovel=imovel)
                unidade = Unidade.objects.get(pk=unidade_id, imovel=imovel)
                
                # Cria nova imagem na unidade copiando o conteúdo
                new_img = ImagemUnidade(unidade=unidade)
                # Lê o arquivo original e salva no novo modelo (isso gera um novo arquivo no disco)
                if img_imovel.imagem:
                    new_img.imagem.save(img_imovel.imagem.name.split('/')[-1], ContentFile(img_imovel.imagem.read()))
                    new_img.save()
                    
                    # Deleta a antiga
                    img_imovel.delete()
                    
                    # messages.success(request, "Imagem movida para a unidade.")
            except Exception as e:
                print(f"Erro ao mover imagem: {e}")
                # messages.error(request, "Erro ao mover imagem.")
            
            return redirect('custom_admin_imovel_imagens', imovel_id=imovel.id)

    else:
        form = ImovelImagensForm()
    
    imagens_existentes = imovel.imagens.all()
    # Busca unidades para o modal de transferência
    unidades = imovel.unidades.all()
    
    return render(request, 'custom_admin/imovel_imagens.html', {
        'imovel': imovel,
        'form': form,
        'imagens': imagens_existentes,
        'unidades': unidades
    })

@staff_member_required
def custom_admin_delete_imagem(request, imagem_id):
    imagem = get_object_or_404(ImagemImovel, pk=imagem_id)
    imovel_id = imagem.imovel.id
    imagem.delete()
    return redirect('custom_admin_imovel_imagens', imovel_id=imovel_id)

@staff_member_required
def custom_admin_imovel_arquivos(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            form = ImovelArquivosForm(request.POST, request.FILES)
            if form.is_valid():
                arquivos = request.FILES.getlist('arquivos')
                for f in arquivos:
                    # Tenta limpar o nome do arquivo
                    safe_name = slugify(f.name.split('.')[0])
                    ext = f.name.split('.')[-1]
                    f.name = f"{safe_name}.{ext}"
                    ArquivoImovel.objects.create(imovel=imovel, arquivo=f, nome=f.name)
                return redirect('custom_admin_imovel_arquivos', imovel_id=imovel.id)
        
    else:
        form = ImovelArquivosForm()
    
    arquivos_existentes = imovel.arquivos.all()
    return render(request, 'custom_admin/imovel_arquivos.html', {
        'imovel': imovel,
        'form': form,
        'arquivos': arquivos_existentes
    })

@staff_member_required
def custom_admin_delete_arquivo(request, arquivo_id):
    arquivo = get_object_or_404(ArquivoImovel, pk=arquivo_id)
    imovel_id = arquivo.imovel.id
    arquivo.delete()
    return redirect('custom_admin_imovel_arquivos', imovel_id=imovel_id)

@staff_member_required
def custom_admin_imovel_unidades(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    unidades = imovel.unidades.all()
    return render(request, 'custom_admin/imovel_unidades.html', {'imovel': imovel, 'unidades': unidades})

@staff_member_required
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

@staff_member_required
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

@staff_member_required
def custom_admin_delete_unidade(request, unidade_id):
    unidade = get_object_or_404(Unidade, pk=unidade_id)
    imovel_id = unidade.imovel.id
    unidade.delete()
    return redirect('custom_admin_imovel_unidades', imovel_id=imovel_id)

@staff_member_required
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

@staff_member_required
def custom_admin_criar_instalacao(request):
    if request.method == 'POST':
        form = InstalacaoForm(request.POST)
        if form.is_valid():
            form.save()
            # Retorna para a página anterior ou para admin index se não houver referer
            next_url = request.META.get('HTTP_REFERER', 'custom_admin_imoveis_list')
            return redirect(next_url)
    return redirect('custom_admin_imoveis_list')

@staff_member_required
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

from .orulo_service import importar_imoveis_orulo, sincronizar_imovel_orulo
from django.contrib import messages

@staff_member_required
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

import threading

# Estado global para progresso (Em produção, use Redis/Cache)
IMPORT_STATUS = {
    'running': False,
    'progress': 0,
    'message': 'Aguardando...',
    'total': 0,
    'success': False
}

def update_progress(percent, message):
    IMPORT_STATUS['progress'] = percent
    IMPORT_STATUS['message'] = message

def run_import_thread(paginas=1):
    from .orulo_service import importar_imoveis_orulo
    global IMPORT_STATUS
    
    IMPORT_STATUS['running'] = True
    IMPORT_STATUS['progress'] = 0
    IMPORT_STATUS['message'] = 'Iniciando...'
    
    try:
        sucesso, mensagem, total = importar_imoveis_orulo(paginas=paginas, progress_callback=update_progress)
        IMPORT_STATUS['success'] = sucesso
        IMPORT_STATUS['message'] = mensagem
        IMPORT_STATUS['total'] = total
    except Exception as e:
        IMPORT_STATUS['success'] = False
        IMPORT_STATUS['message'] = f"Erro: {str(e)}"
    finally:
        IMPORT_STATUS['running'] = False
        IMPORT_STATUS['progress'] = 100

@staff_member_required
def check_import_progress(request):
    return JsonResponse(IMPORT_STATUS)

@staff_member_required
def custom_admin_importar_orulo(request):
    """View para página de importação da Órulo"""
    
    if request.method == 'POST':
        # Se já estiver rodando, não inicia outro
        if IMPORT_STATUS['running']:
            return JsonResponse({'status': 'error', 'message': 'Já existe uma importação em andamento.'})

        # Inicia thread
        t = threading.Thread(target=run_import_thread, kwargs={'paginas': 1})
        t.daemon = True
        t.start()
        
        return JsonResponse({'status': 'started'})

    return render(request, 'custom_admin/importar_orulo.html', {})

@staff_member_required
def custom_admin_orulo_list(request):
    """
    Lista específica para imóveis importados da Órulo.
    """
    imoveis_list = Imovel.objects.filter(is_orulo=True).order_by('-criado_em')

    # Filtros
    titulo = request.GET.get('titulo')
    bairro = request.GET.get('bairro')
    
    if titulo:
        imoveis_list = imoveis_list.filter(Q(titulo__icontains=titulo) | Q(slug__icontains=slugify(titulo)))
    
    if bairro:
        imoveis_list = imoveis_list.filter(Q(bairro__icontains=bairro) | Q(slug__icontains=slugify(bairro)))

    paginator = Paginator(imoveis_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'imoveis': page_obj, 
        'page_obj': page_obj,
        'titulo_filtro': titulo,
        'bairro_filtro': bairro,
    }

    return render(request, 'custom_admin/orulo_list.html', context)