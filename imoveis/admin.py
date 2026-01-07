from django.contrib import admin
from .models import Imovel

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'bairro',
        'tipo',
        'preco',
        'ativo'
    )

    list_filter = ('tipo', 'ativo', 'bairro')
    search_fields = ('titulo', 'bairro')
    list_editable = ('ativo',)
