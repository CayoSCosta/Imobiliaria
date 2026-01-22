from django.conf import settings
from .models import Imovel

def whatsapp_settings(request):
    return {
        'WHATSAPP_NUMERO': settings.WHATSAPP_NUMERO
    }

def bairros_footer(request):
    # Obtém todos os bairros distintos de imóveis ativos, ordenados alfabeticamente
    bairros = Imovel.objects.filter(ativo=True).values_list('bairro', flat=True).distinct().order_by('bairro')
    return {
        'bairros_footer': bairros
    }
