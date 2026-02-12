from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from imoveis.sitemaps import ImovelSitemap, StaticViewSitemap

sitemaps = {
    'imoveis': ImovelSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # ADMIN
    path('painel/', admin.site.urls),
    
    # AUTH
    path('accounts/', include('django.contrib.auth.urls')),

    # Rota para testar o template 404 (apenas para visualização em desenvolvimento)
    path('404/', TemplateView.as_view(template_name='404.html'), name='test_404'),

    # FRONT + API
    path('', include('imoveis.urls')),
    path('', include('leads.urls')),
    path('', include('blog.urls')),
    path('', include('audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
