from rest_framework import generics
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.utils import timezone
from django.contrib import messages
from .models import Lead, Acompanhamento
from .serializers import LeadSerializer
from .forms import AcompanhamentoForm
from imoveis.models import Imovel

class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


@csrf_exempt
@require_POST
def registrar_whatsapp_contato(request):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        data = {}

    imovel_id = data.get('imovel')
    origem = data.get('origem') or 'WhatsApp'
    mensagem = data.get('mensagem') or 'Contato via WhatsApp'
    nome = data.get('nome') or 'Contato via WhatsApp'
    telefone = data.get('telefone') or 'Não informado'
    email = data.get('email')

    imovel = None
    if imovel_id:
        imovel = Imovel.objects.filter(id=imovel_id).first()

    Lead.objects.create(
        nome=nome,
        telefone=telefone,
        email=email,
        origem=origem,
        tipo_contato='whatsapp',
        mensagem=mensagem,
        imovel=imovel,
        status='novo',
    )

    return JsonResponse({'success': True})

@staff_member_required
def custom_admin_leads_list(request):
    leads = Lead.objects.filter(ativo=True).order_by('-data_criacao')
    
    # Organiza os leads por status para o Kanban
    kanban_data = {
        'novo': leads.filter(status='novo'),
        'em_atendimento': leads.filter(status='em_atendimento'),
        'visita_agendada': leads.filter(status='visita_agendada'),
        'proposta': leads.filter(status='proposta'),
        'fechado': leads.filter(status='fechado'),
        'perdido': leads.filter(status='perdido'),
    }
    
    return render(request, 'custom_admin/leads_list.html', {
        'kanban_data': kanban_data,
        'status_choices': Lead.STATUS_CHOICES
    })

@staff_member_required
@require_POST
def update_lead_status(request, pk):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(Lead.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
            
        lead = get_object_or_404(Lead, pk=pk)
        lead.status = new_status
        # Se for fechado ou perdido, podemos marcar como atendido também, se quisermos manter a compatibilidade
        if new_status in ['fechado', 'perdido']:
            lead.atendido = True
        elif new_status == 'novo':
            lead.atendido = False
        else:
            lead.atendido = True # Considera em atendimento
            
        lead.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
def custom_admin_lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    acompanhamentos_list = lead.acompanhamentos.all()
    
    # Paginação
    paginator = Paginator(acompanhamentos_list, 5) # 5 acompanhamentos por página
    page_number = request.GET.get('page')
    acompanhamentos = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = AcompanhamentoForm(request.POST)
        if form.is_valid():
            acompanhamento = form.save(commit=False)
            acompanhamento.lead = lead
            acompanhamento.save()
            return redirect('custom_admin_lead_detail', pk=pk)
    else:
        form = AcompanhamentoForm()

    return render(request, 'custom_admin/lead_detail.html', {
        'lead': lead,
        'acompanhamentos': acompanhamentos,
        'form': form
    })


@staff_member_required
def exportar_leads_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="leads_relatorio_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    # BOM para Excel abrir corretamente com acentos/UTF-8
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Cabeçalho
    writer.writerow(['Nome', 'Data e Hora', 'Canal de Chegada', 'Telefone', 'Email', 'Status'])

    leads = Lead.objects.all().select_related('imovel').order_by('-data_criacao')

    for lead in leads:
        # Lógica do Canal de Chegada (Replicando o card do Kanban)
        canal = 'Fale Conosco'
        
        if lead.imovel:
            canal = f"Imóvel: {lead.imovel.titulo}"
        elif lead.mensagem:
            if "Simulador de Financiamento" in lead.mensagem:
                canal = "Simulador Financiamento"
            elif "Simulador Minha Casa Minha Vida" in lead.mensagem:
                canal = "Simulador MCMV"
        
        # Fallback para o campo origem se não for nenhum dos acima e tiver valor diferente do padrão
        if canal == 'Fale Conosco' and lead.origem and lead.origem != 'Site':
             canal = lead.origem

        data_hora = lead.data_criacao.strftime('%d/%m/%Y %H:%M')
        
        writer.writerow([
            lead.nome,
            data_hora,
            canal,
            lead.telefone,
            lead.email or '',
            lead.get_status_display()
        ])

    return response

@staff_member_required
@require_POST
def custom_admin_delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    messages.success(request, "Lead excluído permanentemente.")
    return redirect('custom_admin_leads_list')

@staff_member_required
@require_POST
def custom_admin_inactivate_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.ativo = False
    lead.save()
    messages.success(request, "Lead arquivado com sucesso.")
    return redirect('custom_admin_leads_list')
