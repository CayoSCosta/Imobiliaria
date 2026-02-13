from django import template
from django.db.models import Prefetch
from imoveis.models import Imovel, ImagemImovel

register = template.Library()

@register.inclusion_tag('blog/partials/sidebar_imoveis_destaque.html')
def exibir_imoveis_destaque(count=3):
    """
    Busca imóveis marcados como destaque para exibir na sidebar do blog.
    Prioriza: Imoveis marcados com destaque_blog
    """
    imoveis = Imovel.objects.filter(
        destaque_blog=True,
        ativo=True
    ).prefetch_related(
        Prefetch('imagens', queryset=ImagemImovel.objects.filter(principal=True), to_attr='capa_lista')
    ).defer(
        'descricao', 'seo_description', 'seo_title', 'latitude', 'longitude', 
        'orulo_id', 'removido_na_origem'
    ).order_by('-criado_em')[:count]
    
    return {'imoveis_destaque': imoveis}
