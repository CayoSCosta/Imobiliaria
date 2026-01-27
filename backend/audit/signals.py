from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from .models import AuditLog
from .middleware import get_current_request, get_current_user
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json
from decimal import Decimal
from datetime import date, datetime, time
from uuid import UUID
from django.db.models.fields.files import FieldFile

# Convert objects to serializable format
def clean_value(value):
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, FieldFile):
        return value.name or ''
    if hasattr(value, 'id'): # Foreign Keys
        return value.id
    if hasattr(value, 'all'): # ManyRelatedManager (skipped in model_to_dict usually but just in case)
        return [clean_value(v) for v in value.all()]
    return value

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

IGNORED_MODELS = [
    'audit.auditlog', 
    'admin.logentry', 
    'sessions.session', 
    'contenttypes.contenttype',
    'auth.permission',
    'auth.group_permissions', # m2m table
    # Add other system models to ignore
]

def should_audit(sender):
    label = sender._meta.label_lower
    if label in IGNORED_MODELS:
        return False
    if label.startswith('migrations.'):
        return False
    return True

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not should_audit(sender):
        return
        
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            # Use model_to_dict but might need explicit handling for fields not covered
            # For simplicity we assume model_to_dict covers standard fields
            instance._old_state = model_to_dict(old_instance)
        except sender.DoesNotExist:
            instance._old_state = {}
    else:
        instance._old_state = {}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not should_audit(sender):
        return
        
    request = get_current_request()
    
    # If explicit user is set on instance (e.g. CLI scripts), use it, else request user
    user = getattr(instance, '_current_user', get_current_user())
    
    changes = {}
    new_state = model_to_dict(instance)
    
    if created:
        action = AuditLog.ACTION_CREATE
        for key, value in new_state.items():
            changes[key] = clean_value(value)
    else:
        action = AuditLog.ACTION_UPDATE
        old_state = getattr(instance, '_old_state', {})
        for key, value in new_state.items():
            val_cleaned = clean_value(value)
            old_val_cleaned = clean_value(old_state.get(key))
            
            if old_val_cleaned != val_cleaned:
                changes[key] = [old_val_cleaned, val_cleaned]
    
    if not changes and not created:
        return 

    # Prepare data
    ip = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if request else None
    path = request.path[:255] if request else None
    
    content_type = ContentType.objects.get_for_model(sender)
    
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        user_email=user.email if user and user.is_authenticated else '',
        action=action,
        changes=json.loads(json.dumps(changes, cls=DjangoJSONEncoder)),
        content_type=content_type,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        ip_address=ip,
        user_agent=user_agent,
        path=path
    )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not should_audit(sender):
        return
        
    request = get_current_request()
    user = get_current_user()
    ip = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if request else None
    path = request.path[:255] if request else None

    state = model_to_dict(instance)
    changes = {k: clean_value(v) for k, v in state.items()}

    content_type = ContentType.objects.get_for_model(sender)

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        user_email=user.email if user and user.is_authenticated else '',
        action=AuditLog.ACTION_DELETE,
        changes=json.loads(json.dumps(changes, cls=DjangoJSONEncoder)),
        content_type=content_type,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        ip_address=ip,
        user_agent=user_agent,
        path=path
    )
