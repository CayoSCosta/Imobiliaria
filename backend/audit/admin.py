from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'content_type', 'object_repr', 'ip_address')
    list_filter = ('action', 'timestamp', 'content_type')
    search_fields = ('user__username', 'user__email', 'object_repr', 'object_id', 'changes')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True # Admin pode limpar logs se necessario, ou mudar para False para log imutavel
