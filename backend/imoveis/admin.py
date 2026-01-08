from django.contrib import admin
from .models import Imovel, ImagemImovel


class ImagemImovelInline(admin.TabularInline):
    model = ImagemImovel
    extra = 1
    fields = ('imagem', 'principal', 'ordem')
    ordering = ('ordem',)


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'bairro', 'tipo', 'preco', 'ativo'
    )
    list_filter = (
        'tipo', 'bairro', 'ativo'
    )
    search_fields = (
        'titulo', 'descricao', 'bairro'
    )
    inlines = [ImagemImovelInline]

@admin.register(ImagemImovel)
class ImagemImovelAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'principal', 'ordem')
    list_filter = ('principal',)
