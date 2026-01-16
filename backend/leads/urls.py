from django.urls import path
from .views import LeadCreateView, custom_admin_leads_list, custom_admin_lead_detail

urlpatterns = [
    path('api/leads/', LeadCreateView.as_view(), name='lead-create'),
    path('custom-admin/leads/', custom_admin_leads_list, name='custom_admin_leads_list'),
    path('custom-admin/leads/<int:pk>/', custom_admin_lead_detail, name='custom_admin_lead_detail'),
]
