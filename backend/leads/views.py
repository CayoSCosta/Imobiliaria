from rest_framework import generics
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from .models import Lead, Acompanhamento
from .serializers import LeadSerializer
from .forms import AcompanhamentoForm

class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

@staff_member_required
def custom_admin_leads_list(request):
    leads = Lead.objects.all().order_by('-data_criacao')
    return render(request, 'custom_admin/leads_list.html', {'leads': leads})

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

