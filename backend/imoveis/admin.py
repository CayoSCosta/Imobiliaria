from django.contrib import admin
from django import forms # <--- Certifique-se de que isso está no topo
from django.db import models
from django.utils.html import format_html
from .models import Imovel, Instalacao, Unidade, ImagemImovel, ImagemUnidade

# =========================
# 1. FORMULÁRIO DE FILTRO (Adicione isso no topo)
# =========================
class ImagemUnidadeForm(forms.ModelForm):
    imovel = forms.ModelChoiceField(
        queryset=Imovel.objects.all(),
        required=False,
        label="1. Escolha o Empreendimento"
    )

    class Meta:
        model = ImagemUnidade
        fields = ['imovel', 'unidade', 'imagem', 'principal', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.unidade:
            self.fields['imovel'].initial = self.instance.unidade.imovel

# =========================
# HELPER PARA PREVIEW
# =========================
class ImagePreviewMixin:
    def preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.imagem.url)
        return "-"
    preview.short_description = 'Ver'

# =========================
# FILTRO DE PREÇO
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
# INLINES
# =========================
class ImagemImovelInline(admin.TabularInline, ImagePreviewMixin):
    model = ImagemImovel
    extra = 3
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
# ADMINS (MANTENHA ESTES)
# =========================
@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin): 
    # Remova o 'preview' da lista por enquanto para o erro sumir
    list_display = ('titulo', 'imovel', 'preco', 'quartos', 'area_m2', 'ativo')
    list_filter = ('ativo', 'quartos', 'imovel')
    inlines = [ImagemUnidadeInline]

@admin.register(Instalacao)
class InstalacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'icone')
    search_fields = ('nome',)

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'destaque', 'bairro', 'cidade', 'tipo', 'ativo', 'criado_em')
    list_editable = ('destaque', 'ativo')
    list_filter = (FaixaPrecoFilter, 'destaque', 'tipo', 'bairro', 'ativo')
    prepopulated_fields = {"slug": ("titulo", "bairro")}
    inlines = [UnidadeInline, ImagemImovelInline]
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

# =========================
# REGISTROS DE IMAGENS (AQUI MUDOU)
# =========================
@admin.register(ImagemUnidade)
class ImagemUnidadeAdmin(admin.ModelAdmin, ImagePreviewMixin):
    form = ImagemUnidadeForm
    list_display = ('preview', 'unidade', 'get_imovel', 'principal', 'ordem')
    list_filter = ('unidade__imovel', 'principal')
    
    def get_imovel(self, obj):
        return obj.unidade.imovel
    get_imovel.short_description = 'Empreendimento'

    class Media:
        js = ('admin/js/vendor/jquery/jquery.js', 'js/remover_unidades.js')

admin.site.register(ImagemImovel)