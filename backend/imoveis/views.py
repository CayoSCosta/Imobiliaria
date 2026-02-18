from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Min, Max, Q, F, Value, FloatField, Count
from django.db.models.functions import ACos, Cos, Radians, Sin, Cast
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Imovel, Unidade, ImagemImovel, Instalacao, ImagemUnidade, ArquivoImovel, Visita
from .serializers import ImovelSerializer
from django.http import JsonResponse, HttpResponse
from leads.models import Lead
from .forms import (
    ImovelImagensForm, 
    UnidadeForm, 
    ImovelInstalacoesForm, 
    ImovelForm,
    InstalacaoForm,
    ImovelArquivosForm
)
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime

# =========================
# FRONTEND (HTML)
# =========================
from django.core.paginator import Paginator
from urllib.parse import quote
import re

def index(request):
    imoveis = Imovel.objects.filter(ativo=True).annotate(
        min_quartos=Min('unidades__quartos'),
        max_quartos=Max('unidades__quartos'), 
        min_area=Min('unidades__area_m2'),
        max_area=Max('unidades__area_m2')     
    ).prefetch_related('imagens', 'unidades')

    # Hero (Carrossel): segue somente a priorização manual por ordem_exibicao.
    destaques = imoveis.order_by('ordem_exibicao', '-id')[:5]

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
    km = request.GET.get('km', '0')
    geo_ativo = False

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

            km_float = float(km)
            if km_float > 0:
                imoveis = imoveis.filter(distance__lte=km_float)

            geo_ativo = True
            
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
        imoveis = imoveis.filter(preco__gte=preco_min).distinct()

    if preco_max:
        imoveis = imoveis.filter(preco__lte=preco_max).distinct()

    # Ordenação padrão para garantir consistência na paginação
    # usando ordem manual definida no gerenciador.
    if not geo_ativo:
        imoveis = imoveis.order_by('ordem_exibicao', '-id')

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
        'lat_selecionada': lat,
        'lng_selecionada': lng,
        'km_selecionado': km,
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
            email=email,
            origem='Simulador Financiamento',
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
            email=email,
            origem='Simulador MCMV',
            mensagem=conteudo,
            status='novo'
        )
        return JsonResponse({'success': True})

    return render(request, 'simuladores/mcmv.html')

def pagina_mcmv(request):
    # Imóveis do tipo Minha Casa Minha Vida
    imoveis = Imovel.objects.filter(ativo=True, tipo='MCMV').prefetch_related('imagens', 'unidades').annotate(
        min_quartos=Min('unidades__quartos'),
        max_quartos=Max('unidades__quartos'), 
        min_area=Min('unidades__area_m2'),
        max_area=Max('unidades__area_m2')     
    ).order_by('-criado_em')

    return render(request, 'imoveis/pagina_mcmv.html', {'imoveis': imoveis})

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
            email=email,
            origem='Fale Conosco',
            mensagem=conteudo_completo,
            tipo_contato='whatsapp', # Padrão
            status='novo'
        )

        return render(request, 'institucional/fale_conosco.html', {'sucesso': True})
    return render(request, 'institucional/fale_conosco.html')

def imovel_detalhe(request, slug):
# Adicionamos 'unidades__imagens' para trazer as fotos de cada planta
    imovel = get_object_or_404(
        Imovel.objects.prefetch_related('unidades__imagens', 'imagens').annotate(
            min_area=Min('unidades__area_m2'),
            max_area=Max('unidades__area_m2'),
            min_quartos=Min('unidades__quartos'),
            max_quartos=Max('unidades__quartos'),
            min_suites=Min('unidades__suites'),
            max_suites=Max('unidades__suites'),
            min_banheiros=Min('unidades__banheiros'),
            max_banheiros=Max('unidades__banheiros'),
            min_vagas=Min('unidades__vagas'),
            max_vagas=Max('unidades__vagas'),
        ), 
        slug=slug, 
        ativo=True
    )

    # Registrar visita (Contador de Visualizações)
    session_key = f'viewed_imovel_{imovel.id}'
    if not request.session.get(session_key):
        Visita.objects.create(imovel=imovel)
        request.session[session_key] = True

    whatsapp_numero_limpo = re.sub(r'\D', '', settings.WHATSAPP_NUMERO or '')
    if whatsapp_numero_limpo and not whatsapp_numero_limpo.startswith('55'):
        whatsapp_numero_limpo = f"55{whatsapp_numero_limpo}"

    mensagem = f"Olá, gostaria de mais informações a respeito do imóvel {imovel.titulo}."
    whatsapp_url = (
        f"https://wa.me/{whatsapp_numero_limpo}"
        f"?text={quote(mensagem)}"
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
    """Dashboard principal com gráficos e KPIs"""
    
    # KPIs
    total_imoveis = Imovel.objects.count()
    total_leads = Lead.objects.count()
    
    # Dados para Gráficos
    
    # 1. Imóveis por Tipo
    imoveis_por_tipo = list(Imovel.objects.values('tipo').annotate(total=Count('tipo')).order_by('-total'))
    
    # 2. Imóveis por Status de Obra
    imoveis_por_status = list(Imovel.objects.values('status').annotate(total=Count('status')).order_by('-total'))
    
    # 3. Leads por Status
    leads_por_status = list(Lead.objects.values('status').annotate(total=Count('status')).order_by('-total'))
    
    # 4. Visitas nos últimos 7 dias
    hoje = timezone.now().date()
    data_inicio = hoje - timedelta(days=6)
    
    visitas_por_dia = list(
        Visita.objects.filter(data__range=[data_inicio, hoje])
        .values('data')
        .annotate(total=Count('id'))
        .order_by('data')
    )
    
    # Preencher dias vazios com 0
    visitas_dict = {v['data']: v['total'] for v in visitas_por_dia}
    chart_visitas_labels = []
    chart_visitas_data = []
    
    for i in range(7):
        data = data_inicio + timedelta(days=i)
        chart_visitas_labels.append(data.strftime('%d/%m'))
        chart_visitas_data.append(visitas_dict.get(data, 0))

    # Preparar dados para Chart.js (Arrays)
    
    # Helpers para labels legíveis
    tipo_dict = dict(Imovel.TIPO_CHOICES)
    status_imovel_dict = dict(Imovel.STATUS_CHOICES)
    status_lead_dict = dict(Lead.STATUS_CHOICES)

    context = {
        'total_imoveis': total_imoveis,
        'total_leads': total_leads,
        
        'chart_visitas_labels': chart_visitas_labels,
        'chart_visitas_data': chart_visitas_data,
        
        # Gráfico Imóveis por Tipo (Pie/Doughnut)
        'chart_imovel_tipo_labels': [tipo_dict.get(x['tipo'], x['tipo']) for x in imoveis_por_tipo],
        'chart_imovel_tipo_data': [x['total'] for x in imoveis_por_tipo],
        
        # Gráfico Imóveis por Status (Bar)
        'chart_imovel_status_labels': [status_imovel_dict.get(x['status'], x['status']) for x in imoveis_por_status],
        'chart_imovel_status_data': [x['total'] for x in imoveis_por_status],
        
        # Gráfico Leads por Status (Pie/Doughnut)
        'chart_lead_status_labels': [status_lead_dict.get(x['status'], x['status']) for x in leads_por_status],
        'chart_lead_status_data': [x['total'] for x in leads_por_status],
    }
    
    return render(request, 'custom_admin/dashboard.html', context)

@staff_member_required
def custom_admin_imoveis_list(request):
    imoveis_list = Imovel.objects.all().order_by('ordem_exibicao', '-criado_em')

    # Filtros
    busca = request.GET.get('busca')
    status = request.GET.get('status')

    if busca:
        imoveis_list = imoveis_list.filter(
            Q(titulo__icontains=busca) | 
            Q(bairro__icontains=busca) |
            Q(bairro_oficial__icontains=busca) |
            Q(cidade__icontains=busca) |
            Q(construtora__icontains=busca) |
            Q(slug__icontains=slugify(busca))
        )

    if status:
        imoveis_list = imoveis_list.filter(status=status)
    
    paginator = Paginator(imoveis_list, 10)  # Mostra 10 imóveis por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'imoveis': page_obj, 
        'page_obj': page_obj,
        'busca_filtro': busca,
        'status_filtro': status,
        'status_choices': Imovel.STATUS_CHOICES,
    }

    return render(request, 'custom_admin/imoveis_list.html', context)

@staff_member_required
def custom_admin_priorizar_imoveis(request):
    if request.method == 'POST':
        imoveis = list(Imovel.objects.all().only('id', 'ordem_exibicao'))
        alterados = []

        for imovel in imoveis:
            campo = f'ordem_{imovel.id}'
            valor = request.POST.get(campo)

            try:
                nova_ordem = int(valor)
                if nova_ordem < 0:
                    nova_ordem = 0
            except (TypeError, ValueError):
                nova_ordem = imovel.ordem_exibicao

            if nova_ordem != imovel.ordem_exibicao:
                imovel.ordem_exibicao = nova_ordem
                alterados.append(imovel)

        if alterados:
            Imovel.objects.bulk_update(alterados, ['ordem_exibicao'])
            messages.success(request, 'Prioridades atualizadas com sucesso.')
        else:
            messages.info(request, 'Nenhuma alteração de prioridade foi detectada.')

        return redirect('imoveis:custom_admin_priorizar_imoveis')

    imoveis = Imovel.objects.all().order_by('ordem_exibicao', '-criado_em')
    return render(request, 'custom_admin/priorizar_imoveis.html', {'imoveis': imoveis})

@staff_member_required
def custom_admin_delete_imovel(request, imovel_id):
    """Exclui um imóvel específico"""
    imovel = get_object_or_404(Imovel, id=imovel_id)
    if request.method == 'POST':
        imovel.delete()
        # messages.success(request, f'Imóvel "{imovel.titulo}" excluído com sucesso!') # Se tiver messages
        return redirect('imoveis:custom_admin_imoveis_list')
    
    # Se for GET, não faz nada ou renderiza confirmação (mas vamos usar modal e POST)
    return redirect('imoveis:custom_admin_imoveis_list')

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
        
    return redirect('imoveis:custom_admin_orulo_list')

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
                return redirect('imoveis:custom_admin_imovel_imagens', imovel_id=imovel.id)
        
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
            
            return redirect('imoveis:custom_admin_imovel_imagens', imovel_id=imovel.id)
            
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
            
            return redirect('imoveis:custom_admin_imovel_imagens', imovel_id=imovel.id)

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
    return redirect('imoveis:custom_admin_imovel_imagens', imovel_id=imovel_id)

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
                return redirect('imoveis:custom_admin_imovel_arquivos', imovel_id=imovel.id)
        
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
    return redirect('imoveis:custom_admin_imovel_arquivos', imovel_id=imovel_id)

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

            return redirect('imoveis:custom_admin_imovel_unidades', imovel_id=imovel.id)
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
            
            return redirect('imoveis:custom_admin_imovel_unidades', imovel_id=imovel.id)
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
    return redirect('imoveis:custom_admin_imovel_unidades', imovel_id=imovel_id)

@staff_member_required
def custom_admin_imovel_instalacoes(request, imovel_id):
    imovel = get_object_or_404(Imovel, pk=imovel_id)
    if request.method == 'POST':
        form = ImovelInstalacoesForm(request.POST, instance=imovel)
        if form.is_valid():
            form.save()
            return redirect('imoveis:custom_admin_imovel_instalacoes', imovel_id=imovel.id)
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
            next_url = request.META.get('HTTP_REFERER', 'imoveis:custom_admin_imoveis_list')
            return redirect(next_url)
    return redirect('imoveis:custom_admin_imoveis_list')

@staff_member_required
def custom_admin_criar_imovel(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST)
        if form.is_valid():
            imovel = form.save()
            # Redireciona para a edição de imagens ou lista, vamos para imagens para incentivar o cadastro completo
            return redirect('imoveis:custom_admin_imovel_imagens', imovel_id=imovel.id)
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
            return redirect('imoveis:custom_admin_imoveis_list')
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

@staff_member_required
def custom_admin_exportar_imoveis(request):
    import openpyxl
    from openpyxl.utils import get_column_letter

    # Cria o Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Imóveis Imobidon"

    # Cabeçalho
    headers = [
        "ID", "Título", "Ref. Órulo", "Status", "Bairro", "Cidade", 
        "Preço", "Construtora", "Data Lançamento", "Data Entrega",
        "Área Terreno", "Área Laje", "Unidades/Andar", "Total Unidades", "Andares",
        "Ativo", "Link Público"
    ]
    
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        cell = ws[f"{col_letter}1"]
        cell.value = header
        cell.font = openpyxl.styles.Font(bold=True)

    # Dados
    imoveis = Imovel.objects.all().order_by('-criado_em')
    
    # Aplica filtros se houver (mesma lógica da lista)
    busca = request.GET.get("busca")
    status = request.GET.get("status")
    
    if busca:
        imoveis = imoveis.filter(
            Q(titulo__icontains=busca) | 
            Q(bairro__icontains=busca) | 
            Q(bairro_oficial__icontains=busca) |
            Q(cidade__icontains=busca) | 
            Q(construtora__icontains=busca) |
            Q(slug__icontains=slugify(busca))
        )

    if status:
        imoveis = imoveis.filter(status=status)

    for row_num, imovel in enumerate(imoveis, 2):
        ws.cell(row=row_num, column=1, value=imovel.id)
        ws.cell(row=row_num, column=2, value=imovel.titulo)
        ws.cell(row=row_num, column=3, value=imovel.orulo_id if imovel.orulo_id else "Manual")
        ws.cell(row=row_num, column=4, value=imovel.get_status_display())
        ws.cell(row=row_num, column=5, value=imovel.bairro)
        ws.cell(row=row_num, column=6, value=imovel.cidade)
        ws.cell(row=row_num, column=7, value=float(imovel.preco) if imovel.preco and imovel.preco > 0 else 0)
        ws.cell(row=row_num, column=8, value=imovel.construtora)
        
        # Datas formatadas
        lanc = imovel.data_lancamento.strftime("%d/%m/%Y") if imovel.data_lancamento else ""
        ent = imovel.data_entrega.strftime("%d/%m/%Y") if imovel.data_entrega else ""
        
        ws.cell(row=row_num, column=9, value=lanc)
        ws.cell(row=row_num, column=10, value=ent)
        
        ws.cell(row=row_num, column=11, value=float(imovel.area_total) if imovel.area_total else "")
        ws.cell(row=row_num, column=12, value=float(imovel.area_laje) if imovel.area_laje else "")
        
        ws.cell(row=row_num, column=13, value=imovel.unidades_por_andar)
        ws.cell(row=row_num, column=14, value=imovel.total_unidades)
        ws.cell(row=row_num, column=15, value=imovel.numero_andares)
        
        ws.cell(row=row_num, column=16, value="Sim" if imovel.ativo else "Não")
        
        try:
            link = request.build_absolute_uri(f"/imovel/{imovel.slug}/")
            cell_link = ws.cell(row=row_num, column=17, value=link)
            cell_link.hyperlink = link
            cell_link.style = "Hyperlink"
        except:
             pass

    # Auto-ajuste de colunas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        if adjusted_width > 50: adjusted_width = 50
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = f"imoveis_imobidon_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    
    wb.save(response)
    return response