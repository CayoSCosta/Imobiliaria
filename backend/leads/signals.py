import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead)
def enviar_email_novo_lead(sender, instance, created, **kwargs):
    if not created:
        return

    destinatarios = getattr(settings, 'LEAD_NOTIFICATION_EMAILS', [])
    if not destinatarios:
        return

    imovel_titulo = instance.imovel.titulo if instance.imovel else 'Não informado'

    assunto = f"Novo lead: {instance.nome}"
    corpo = (
        f"Um novo lead foi recebido.\n\n"
        f"Nome: {instance.nome}\n"
        f"Telefone: {instance.telefone}\n"
        f"E-mail: {instance.email or 'Não informado'}\n"
        f"Preferência de contato: {instance.get_tipo_contato_display()}\n"
        f"Origem: {instance.origem}\n"
        f"Imóvel: {imovel_titulo}\n"
        f"Mensagem:\n{instance.mensagem or 'Não informado'}\n\n"
        f"Data/Hora: {instance.data_criacao.strftime('%d/%m/%Y %H:%M')}"
    )

    try:
        send_mail(
            assunto,
            corpo,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            fail_silently=False,
        )
    except Exception:
        logger.exception('Falha ao enviar e-mail de novo lead')
