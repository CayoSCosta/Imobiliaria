from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    
    ACTION_CHOICES = (
        (ACTION_CREATE, 'Criação'),
        (ACTION_UPDATE, 'Atualização'),
        (ACTION_DELETE, 'Exclusão'),
    )

    # Quem fez
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuário'
    )
    user_email = models.EmailField(null=True, blank=True, verbose_name='Email do Usuário (Snapshot)') # Caso o user seja deletado
    
    # O que fez
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Ação')
    changes = models.JSONField(null=True, blank=True, verbose_name='Alterações') # {campo: [valor_antigo, valor_novo]}
    
    # Onde fez (Polymorphic relation)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255) # Char em vez de Int para suportar UUIDs se necessário
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, verbose_name='Representação do Objeto') # __str__ do objeto
    
    # Contexto adicional
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    user_agent = models.CharField(max_length=500, null=True, blank=True, verbose_name='User Agent')
    path = models.CharField(max_length=255, null=True, blank=True, verbose_name='Caminho da URL')
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]
        permissions = [
            ("acesso_painel_admin", "Pode acessar o painel de administração"),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.content_type.model} - {self.timestamp}"
