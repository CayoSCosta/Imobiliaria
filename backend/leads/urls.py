from django.urls import path
from . import views
from .views import LeadCreateView, custom_admin_leads_list, custom_admin_lead_detail, update_lead_status, exportar_leads_csv, registrar_whatsapp_contato

urlpatterns = [
    path('api/leads/', LeadCreateView.as_view(), name='lead-create'),
    path('api/whatsapp-click/', registrar_whatsapp_contato, name='whatsapp-click'),
    path('custom-admin/leads/', custom_admin_leads_list, name='custom_admin_leads_list'),
    path('custom-admin/leads/exportar-csv/', exportar_leads_csv, name='exportar_leads_csv'),
    path('custom-admin/leads/<int:pk>/', custom_admin_lead_detail, name='custom_admin_lead_detail'),
    path('custom-admin/leads/<int:pk>/update-status/', update_lead_status, name='update_lead_status'),
    path('custom-admin/leads/<int:pk>/delete/', views.custom_admin_delete_lead, name='custom_admin_delete_lead'),
    path('custom-admin/leads/<int:pk>/inactivate/', views.custom_admin_inactivate_lead, name='custom_admin_inactivate_lead'),
]
