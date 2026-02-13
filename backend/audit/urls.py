from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('gerenciador/audit/', views.custom_admin_audit_list, name='custom_admin_audit_list'),
    path('gerenciador/audit/<int:log_id>/delete/', views.custom_admin_delete_audit_log, name='custom_admin_delete_audit_log'),
    path('gerenciador/audit/clear/', views.custom_admin_clear_audit_logs, name='custom_admin_clear_audit_logs'),
]
