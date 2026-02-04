from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import AuditLog

@staff_member_required
def custom_admin_audit_list(request):
    logs_list = AuditLog.objects.all().select_related('user', 'content_type')
    
    # Filtros simples (opcional, mas bom ter)
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    
    if user_filter:
        logs_list = logs_list.filter(user__username__icontains=user_filter)
    if action_filter:
        logs_list = logs_list.filter(action=action_filter)

    paginator = Paginator(logs_list, 20)  # Show 20 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'logs': page_obj,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'custom_admin/audit_list.html', context)

@staff_member_required
def custom_admin_delete_audit_log(request, log_id):
    log = get_object_or_404(AuditLog, id=log_id)
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Log de auditoria removido com sucesso.')
    return redirect('custom_admin_audit_list')

@staff_member_required
def custom_admin_clear_audit_logs(request):
    if request.method == 'POST':
        count, _ = AuditLog.objects.all().delete()
        messages.success(request, f'{count} logs de auditoria foram removidos.')
    return redirect('custom_admin_audit_list')
