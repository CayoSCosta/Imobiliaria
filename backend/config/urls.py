from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),
    
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
