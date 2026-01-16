from django.core.management.base import BaseCommand
from imoveis.orulo_service import importar_imoveis_orulo

class Command(BaseCommand):
    help = 'Importa imóveis da API pública da Órulo'

    def add_arguments(self, parser):
        parser.add_argument('--paginas', type=int, default=1, help='Número de páginas para importar')

    def handle(self, *args, **options):
        paginas = options['paginas']
        self.stdout.write(f"Iniciando importação de {paginas} página(s)...")

        sucesso, mensagem, total = importar_imoveis_orulo(paginas=paginas)
        
        if sucesso:
            self.stdout.write(self.style.SUCCESS(f"{mensagem} Total importado: {total}"))
        else:
            self.stdout.write(self.style.ERROR(f"Erro: {mensagem}"))
