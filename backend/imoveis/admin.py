from django.contrib import admin
from django.utils.html import format_html
from .models import Imovel, Unidade, ImagemImovel, ImagemUnidade

# =========================
# HELPER PARA PREVIEW (Opcional, mas ajuda muito)
# =========================
class ImagePreviewMixin:
    def preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.imagem.url)
        return "-"
    preview.short_description = 'Ver'

# =========================
# FILTRO DE PREÇO (Mantenha, ele é seguro)
# =========================
class FaixaPrecoFilter(admin.SimpleListFilter):
    title = 'Faixa de Preço (Unidades)'
    parameter_name = 'faixa_preco'
    def lookups(self, request, model_admin):
        return (
            ('0-300', 'Até R$ 300 mil'),
            ('300-600', 'R$ 300 mil a R$ 600 mil'),
            ('600-1000', 'R$ 600 mil a R$ 1 milhão'),
            ('1000+', 'Acima de R$ 1 milhão'),
        )
    def queryset(self, request, queryset):
        if self.value() == '0-300': return queryset.filter(unidades__preco__lte=300000).distinct()
        if self.value() == '300-600': return queryset.filter(unidades__preco__range=(300000, 600000)).distinct()
        if self.value() == '600-1000': return queryset.filter(unidades__preco__range=(600000, 1000000)).distinct()
        if self.value() == '1000+': return queryset.filter(unidades__preco__gte=1000000).distinct()

# =========================
# INLINES PADRÃO (UM POR UM)
# =========================

class ImagemImovelInline(admin.TabularInline, ImagePreviewMixin):
    model = ImagemImovel
    extra = 3  # Mostra 3 linhas vazias para facilitar o upload de várias seguidas
    fields = ('preview', 'imagem', 'principal', 'ordem')
    readonly_fields = ('preview',)
    ordering = ('ordem',)

class ImagemUnidadeInline(admin.TabularInline, ImagePreviewMixin):
    model = ImagemUnidade
    extra = 3
    fields = ('preview', 'imagem', 'principal', 'ordem')
    readonly_fields = ('preview',)
    ordering = ('ordem',)

class UnidadeInline(admin.TabularInline):
    model = Unidade
    extra = 1
    show_change_link = True
    fields = ('titulo', 'preco', 'area_m2', 'quartos', 'banheiros', 'suites', 'vagas', 'ativo')

# =========================
# ADMINS
# =========================

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('preview', 'titulo', 'imovel', 'preco', 'quartos', 'area_m2', 'ativo')
    list_filter = ('ativo', 'quartos', 'imovel')
    inlines = [ImagemUnidadeInline]

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'bairro', 'cidade', 'tipo', 'ativo', 'criado_em')
    list_filter = (FaixaPrecoFilter, 'tipo', 'bairro', 'ativo')
    prepopulated_fields = {"slug": ("titulo", "bairro")}
    inlines = [UnidadeInline, ImagemImovelInline]

# Registro das imagens separadas caso precise de edição rápida
admin.site.register(ImagemImovel)
admin.site.register(ImagemUnidade)