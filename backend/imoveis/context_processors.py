from django.conf import settings

def whatsapp_settings(request):
    return {
        'WHATSAPP_NUMERO': settings.WHATSAPP_NUMERO
    }
