from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Imovel

class ImovelSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Imovel.objects.filter(ativo=True).order_by('-atualizado_em')

    def lastmod(self, obj):
        return obj.atualizado_em

    def location(self, obj):
        return reverse('imoveis:imovel_detalhe', args=[obj.slug])

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['home', 'sobre_nos', 'termos_de_uso', 'politica_de_privacidade', 'fale_conosco']

    def location(self, item):
        return reverse(f'imoveis:{item}')
