import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from imoveis.models import Imovel, Unidade
from imoveis.orulo_service import get_orulo_auth_header, associar_plantas_a_unidades


class Command(BaseCommand):
    help = 'Atualiza plantas faltantes da Órulo para imóveis já importados (foco em ImagemUnidade).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--imovel-id',
            type=int,
            default=None,
            help='Processa apenas um imóvel específico pelo ID local.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limita a quantidade de imóveis processados (0 = sem limite).',
        )
        parser.add_argument(
            '--max-plans',
            type=int,
            default=10,
            help='Máximo de plantas por imóvel para tentar associar.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Reprocessa mesmo imóveis que já têm plantas em unidades.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula, sem salvar imagens.',
        )

    def handle(self, *args, **options):
        imovel_id = options['imovel_id']
        limit = options['limit']
        max_plans = options['max_plans']
        force = options['force']
        dry_run = options['dry_run']

        headers = get_orulo_auth_header()
        if not headers:
            self.stdout.write(self.style.ERROR('Falha na autenticação com a API da Órulo.'))
            return

        base_url = settings.ORULO_BASE_URL

        qs = Imovel.objects.filter(is_orulo=True).exclude(orulo_id__isnull=True).exclude(orulo_id='').order_by('id')
        if imovel_id:
            qs = qs.filter(id=imovel_id)

        if limit and limit > 0:
            qs = qs[:limit]

        total_alvo = qs.count() if hasattr(qs, 'count') else len(qs)
        self.stdout.write(f'Imóveis alvo: {total_alvo}')
        if dry_run:
            self.stdout.write(self.style.WARNING('Modo DRY-RUN ativo: nada será salvo.'))

        processados = 0
        ignorados_sem_unidade = 0
        ignorados_com_plantas = 0
        sem_planos_orulo = 0
        erros_api = 0
        atualizados = 0
        plantas_associadas = 0

        for imovel in qs:
            processados += 1

            total_unidades = imovel.unidades.count()
            if total_unidades == 0:
                ignorados_sem_unidade += 1
                self.stdout.write(f'[{imovel.id}] {imovel.titulo}: ignorado (sem unidades).')
                continue

            unidades_com_planta = Unidade.objects.filter(imovel=imovel, imagens__isnull=False).distinct().count()
            if unidades_com_planta > 0 and not force:
                ignorados_com_plantas += 1
                self.stdout.write(
                    f'[{imovel.id}] {imovel.titulo}: ignorado (já possui {unidades_com_planta}/{total_unidades} unidade(s) com planta).'
                )
                continue

            url_plans = f"{base_url}/buildings/{imovel.orulo_id}/floor_plans"
            params_plans = {'dimensions[]': '1024x1024'}

            try:
                resp_plans = requests.get(url_plans, headers=headers, params=params_plans, timeout=15)
            except Exception as exc:
                erros_api += 1
                self.stdout.write(self.style.ERROR(f'[{imovel.id}] erro de conexão API: {str(exc)}'))
                continue

            if resp_plans.status_code != 200:
                erros_api += 1
                self.stdout.write(
                    self.style.ERROR(f'[{imovel.id}] API retornou {resp_plans.status_code} ao buscar plantas.')
                )
                continue

            plans = resp_plans.json().get('floor_plans', [])
            if not plans:
                sem_planos_orulo += 1
                self.stdout.write(f'[{imovel.id}] {imovel.titulo}: sem floor_plans na Órulo.')
                continue

            if dry_run:
                self.stdout.write(
                    f'[{imovel.id}] {imovel.titulo}: {len(plans)} planta(s) encontrada(s) para tentativa de associação.'
                )
                continue

            count = associar_plantas_a_unidades(imovel, plans, max_plans=max_plans)
            if count > 0:
                atualizados += 1
                plantas_associadas += count
                self.stdout.write(self.style.SUCCESS(f'[{imovel.id}] {imovel.titulo}: {count} planta(s) associada(s).'))
            else:
                self.stdout.write(f'[{imovel.id}] {imovel.titulo}: nenhuma planta compatível com unidades.')

        self.stdout.write('')
        self.stdout.write('Resumo:')
        self.stdout.write(f'- Processados: {processados}')
        self.stdout.write(f'- Atualizados: {atualizados}')
        self.stdout.write(f'- Plantas associadas: {plantas_associadas}')
        self.stdout.write(f'- Ignorados sem unidades: {ignorados_sem_unidade}')
        self.stdout.write(f'- Ignorados com plantas existentes: {ignorados_com_plantas}')
        self.stdout.write(f'- Sem floor_plans na Órulo: {sem_planos_orulo}')
        self.stdout.write(f'- Erros API: {erros_api}')
