from rest_framework import generics
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Lead
from .serializers import LeadSerializer

class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

@staff_member_required
def custom_admin_leads_list(request):
    leads = Lead.objects.all().order_by('-data_criacao')
    return render(request, 'custom_admin/leads_list.html', {'leads': leads})

