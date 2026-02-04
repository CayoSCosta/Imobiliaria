from django.core.management.base import BaseCommand
from django.utils import timezone
from imoveis.models import Imovel

class Command(BaseCommand):
    help = 'Atualiza o status dos imóveis cuja data de entrega já passou para PRONTO'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando verificação de status dos imóveis...')
        
        today = timezone.localdate()
        
        # Filtra imóveis que NÃO estão prontos e onde data_entrega <= hoje
        imoveis_para_atualizar = Imovel.objects.exclude(
            status='PRONTO'
        ).filter(
            data_entrega__lte=today,
            data_entrega__isnull=False
        )
        
        count = imoveis_para_atualizar.count()
        
        if count > 0:
            # O método update() é mais eficiente que iterar e salvar um por um,
            # mas não chama o método save() sobrescrito no modelo.
            # Como só estamos mudando o status, usei update() aqui.
            updated = imoveis_para_atualizar.update(status='PRONTO')
            self.stdout.write(self.style.SUCCESS(f'Sucesso! {updated} imóveis atualizados para PRONTO.'))
        else:
            self.stdout.write(self.style.SUCCESS('Nenhum imóvel precisou ser atualizado hoje.'))
