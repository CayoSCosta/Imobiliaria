from django.core.exceptions import PermissionDenied

class RestrictAdminMiddleware:
    """
    Middleware para restringir o acesso ao painel de administração (/admin/).
    Permite acesso apenas se:
    1. O usuário é Superusuário.
    2. OU o usuário possui a permissão 'audit.acesso_painel_admin'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                # Superusuário sempre pode
                if request.user.is_superuser:
                    return self.get_response(request)
                
                # Verifica permissão específica
                if request.user.has_perm('audit.acesso_painel_admin'):
                    return self.get_response(request)
                    
                # Se não tem permissão, bloqueia
                raise PermissionDenied("Você não tem permissão para acessar o painel administrativo.")
                
        return self.get_response(request)
