from django.contrib import admin
from .models import Imovel, ImagemImovel


class ImagemImovelInline(admin.TabularInline):
    model = ImagemImovel
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'tipo', 'bairro', 'preco', 'ativo'
    )
    list_filter = (
        'tipo', 'bairro', 'ativo'
    )
    search_fields = (
        'titulo', 'descricao', 'bairro'
    )
    inlines = [ImagemImovelInline]
