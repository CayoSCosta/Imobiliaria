import requests
import re
from django.conf import settings
from django.utils.text import slugify
from django.db import connection, transaction
from django.core.files.base import ContentFile
from .models import Imovel, Unidade, ImagemImovel, ImagemUnidade, Instalacao, ArquivoImovel
from decimal import Decimal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def parse_orulo_date(date_value):
    """
    Tenta converter string de data da Órulo para objeto date do Python.
    Suporta: YYYY-MM-DD, DD/MM/YYYY, MM/YYYY
    """
    if not date_value:
        return None
    
    date_str = str(date_value).strip()
    
    formats = [
        '%Y-%m-%d',      # 2022-09-15
        '%d/%m/%Y',      # 15/09/2022
        '%d-%m-%Y',      # 15-09-2022
        '%Y/%m/%d',      # 2022/09/15
        '%m/%Y',         # 09/2022
        '%Y-%m',         # 2022-09
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue
            
    return None

def fix_sequences():
    """
    Corrige as sequências do PostgreSQL para evitar erro de chave duplicada.
    Isso acontece quando dados são inseridos com IDs explícitos e a sequence fica para trás.
    """
    if connection.vendor == 'postgresql':
        try:
            with connection.cursor() as cursor:
                tables = ['imoveis_instalacao', 'imoveis_imovel', 'imoveis_unidade', 'imoveis_imagemimovel']
                for table in tables:
                    # Ajusta o valor atual da sequence para o MAX(id) da tabela
                    cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM {table};")
        except Exception as e:
            logger.warning(f"Erro ao tentar corrigir sequências do banco: {str(e)}")

def get_orulo_auth_header():
    """
    Obtém o token de acesso via Client Credentials flow.
    """
    url = "https://www.orulo.com.br/oauth/token"
    # Certifique-se de que essas chaves estejam no settings.py
    payload = {
        "client_id": settings.ORULO_CLIENT_ID,
        "client_secret": settings.ORULO_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}
    except requests.RequestException as e:
        logger.error(f"Erro na autenticação Órulo: {str(e)}")
        return None

def associar_plantas_a_unidades(imovel, plans, max_plans=10):
    """
    Tenta associar floor plans às unidades do imóvel pela área descrita na planta.
    Retorna a quantidade de plantas associadas.
    """
    if not plans:
        return 0

    unidades = list(imovel.unidades.all())
    if not unidades:
        return 0

    count_plans = 0

    for j, plan in enumerate(plans[:max_plans]):
        plan_url = plan.get('1024x1024') or plan.get('520x280')
        plan_desc = str(plan.get('description', '')).lower()

        if not plan_url:
            continue

        try:
            r = requests.get(plan_url, timeout=10)
            if r.status_code != 200:
                continue

            area_candidates = re.findall(r'(\d+(?:[.,]\d+)?)\s*m', plan_desc)
            matched_unit = False

            for unidade in unidades:
                area_int = int(unidade.area_m2)
                is_match = False

                for cand in area_candidates:
                    try:
                        cand_float = float(cand.replace(',', '.'))
                        if int(cand_float) == area_int or round(cand_float) == area_int:
                            is_match = True
                            break
                    except Exception:
                        continue

                if not is_match:
                    if (f" {area_int} " in f" {plan_desc} ") or \
                       (f"{area_int}m" in plan_desc) or \
                       (f"{area_int} m" in plan_desc):
                        is_match = True

                if is_match:
                    filename = f"plan_unit_{unidade.id}_{j}.jpg"
                    img_unit = ImagemUnidade(unidade=unidade, principal=False, ordem=j)
                    img_unit.imagem.save(filename, ContentFile(r.content), save=True)
                    matched_unit = True

            if matched_unit:
                count_plans += 1

        except Exception:
            continue

    return count_plans

def importar_imoveis_orulo(paginas=1, progress_callback=None):
    """
    Importa imóveis da API (Endpoint Buildings).
    progress_callback: Função(percent, message) para reportar progresso
    """
    headers = get_orulo_auth_header()
    if not headers:
        return False, "Falha na autenticação.", 0

    base_url = settings.ORULO_BASE_URL
    total_importados = 0
    
    logger.info(f"Iniciando importação de {paginas} páginas da Órulo...")
    
    if progress_callback:
        progress_callback(0, "Verificando banco de dados...")
        
    fix_sequences()
    
    if progress_callback:
        progress_callback(0, "Iniciando autenticação...")

    for page in range(1, paginas + 1):
        try:
            if progress_callback:
                progress_callback(int(((page-1)/paginas)*100), f"Baixando página {page} de {paginas}...")
                
            # Busca lista de empreendimentos
            # Ordenando por data de atualização para pegar os mais recentes
            url = f"{base_url}/buildings?page={page}&results_per_page=12&last_updated_date_order=desc"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Erro API Órulo (Page {page}): {response.status_code} - {response.text}")
                continue
                
            data = response.json()
            buildings = data.get('buildings', [])
            total_items_page = len(buildings)
            
            if not buildings:
                logger.warning(f"Nenhum building encontrado na página {page}")
                break

            for idx, building in enumerate(buildings):
                # Calcula progresso intra-página
                if progress_callback:
                    base_progress = ((page-1)/paginas)*100
                    item_progress = (idx / max(total_items_page, 1)) * (100/paginas)
                    current_percent = int(base_progress + item_progress)
                    progress_callback(current_percent, f"Processando: {building.get('name', 'Imóvel')}")

                nome = building.get('name')
                orulo_id = str(building.get('id'))

                # Verifica se já existe
                imovel = Imovel.objects.filter(orulo_id=orulo_id).first()
                if not imovel:
                    imovel = Imovel.objects.filter(titulo=nome).first()
                    if imovel:
                        imovel.orulo_id = orulo_id
                        imovel.save()

                # Se já existe e tem imagens, pula (otimização)
                # Se não tem imagens, prossegue para corrigir
                if imovel and imovel.imagens.exists():
                    continue

                # Se existe (e vamos re-importar), limpa dependências para evitar duplicidade
                if imovel:
                    imovel.imagens.all().delete()
                    imovel.unidades.all().delete()

                # Mapeamento do Status
                status_api = str(building.get('status', '')).lower()
                status_imovel = 'EM_OBRA'
                # Se contiver 'pronto', 'used' ou 'ready', consideramos Pronto
                if any(x in status_api for x in ['pronto', 'ready', 'used']):
                    status_imovel = 'PRONTO'
                
                # Endereço
                address = building.get('address', {})
                district = address.get('area') or address.get('district') or ''
                city = address.get('city', 'São Paulo')
                state = address.get('state', 'SP')
                street = address.get('street', '')
                number = address.get('number', '')
                zip_code = address.get('zip_code', '')
                latitude = address.get('latitude')
                longitude = address.get('longitude')
                
                # Definição do Tipo e Preço
                min_price = building.get('min_price') or 0
                tipo_imovel = 'MEDIO'
                preco_float = float(min_price)
                
                if preco_float > 0:
                    if preco_float < 350000:
                        tipo_imovel = 'MCMV'
                    elif preco_float > 1500000:
                        tipo_imovel = 'ALTO'

                # Criar ou Atualizar Dados Básicos
                if imovel:
                    imovel.titulo = nome
                    imovel.descricao = building.get('description') or f"Empreendimento {nome}."
                    imovel.tipo = tipo_imovel
                    imovel.status = status_imovel
                    imovel.preco = Decimal(min_price) if float(min_price or 0) > 0 else imovel.preco
                    imovel.bairro = district
                    imovel.bairro_oficial = address.get('area')
                    imovel.cidade = city
                    imovel.uf = state
                    imovel.rua = street
                    imovel.numero = str(number)
                    imovel.cep = zip_code
                    if latitude: imovel.latitude = Decimal(str(latitude))
                    if longitude: imovel.longitude = Decimal(str(longitude))
                    imovel.is_orulo = True
                    # imovel.ativo = True # Manter o estado atual de ativo se já existe
                    imovel.save()
                else:
                    imovel = Imovel.objects.create(
                        titulo=nome,
                        descricao=building.get('description') or f"Empreendimento {nome}.",
                        tipo=tipo_imovel,
                        status=status_imovel,
                        preco=Decimal(min_price) if float(min_price or 0) > 0 else None,
                        bairro=district,
                        bairro_oficial=address.get('area'),
                        cidade=city,
                        uf=state,
                        rua=street,
                        numero=str(number),
                        cep=zip_code,
                        latitude=Decimal(str(latitude)) if latitude else None,
                        longitude=Decimal(str(longitude)) if longitude else None,
                        orulo_id=orulo_id,
                        is_orulo=True,
                        ativo=True
                    )

                # --- Importar Features (Instalações) ---
                features_list = building.get('features', [])
                for feat_name in features_list:
                    # Cria ou pega a instalação pelo nome
                    instalacao_obj, created = Instalacao.objects.get_or_create(nome=feat_name)
                    imovel.instalacoes.add(instalacao_obj)

                # --- Importar Tipologias e Criar Unidades (Novo) ---
                try:
                    url_typologies = f"{base_url}/buildings/{orulo_id}/typologies"
                    # Tenta trazer também tipologias sem estoque se o plano permitir
                    resp_typ = requests.get(url_typologies, headers=headers, params={'include[]': 'not_available'}, timeout=10)
                    
                    if resp_typ.status_code == 200:
                        typologies_data = resp_typ.json().get('typologies', [])
                        
                        for typology in typologies_data:
                            # Tenta evitar duplicidade se já existir unidade semelhante (opcional)
                            # Aqui criamos todas
                            
                            price = typology.get('discount_price') or typology.get('original_price') or 0
                            area = typology.get('private_area') or typology.get('total_area') or 0
                            
                            if float(price) > 0:
                                Unidade.objects.create(
                                    imovel=imovel,
                                    titulo=f"{typology.get('type', 'Unidade')} - {typology.get('reference', '') or typology.get('id')}",
                                    area_m2=int(area),
                                    quartos=int(typology.get('bedrooms', 0)),
                                    banheiros=int(typology.get('bathrooms', 0)),
                                    suites=int(typology.get('suites', 0)),
                                    vagas=int(typology.get('parking', 0)),
                                    ativo=True
                                )
                    else:
                        # Fallback antigo se falhar typologies ou for vazio
                        pass 

                except Exception as ex_typ:
                    logger.warning(f"Erro ao buscar tipologias do imóvel {orulo_id}: {str(ex_typ)}")

                # Se não criou nenhuma unidade via tipologia, usamos o método antigo (fallback)
                if not imovel.unidades.exists():
                     # --- Criar Unidade Representativa "A partir de" ---
                    min_price = building.get('min_price') or 0
                    # A API retorna inteiros diretos como min_bedrooms, min_area, etc.
                    min_area = building.get('min_area') or 0
                    quartos = building.get('min_bedrooms') or 0
                    suites = building.get('min_suites') or 0
                    vagas = building.get('min_parking') or 0
                    banheiros = building.get('min_bathrooms') or 0
                    
                    if banheiros == 0 and suites > 0:
                         banheiros = suites
                    if banheiros == 0:
                         banheiros = 1 # Fallback

                    if min_price:
                        Unidade.objects.create(
                            imovel=imovel,
                            titulo=f"Unidade Padrão - {nome}",
                            area_m2=int(min_area),
                            quartos=int(quartos),
                            banheiros=int(banheiros),
                            suites=int(suites),
                            vagas=int(vagas),
                            ativo=True
                        )
                
                # --- Importar Imagens (Endpoint Novo) ---
                imported_images_count = 0
                images_list = []
                
                # 1. Tenta endpoint de imagens dedicado
                try:
                   url_images = f"{base_url}/buildings/{orulo_id}/images"
                   # A API exige dimensions[]
                   params_img = {'dimensions[]': '1024x1024'} 
                   resp_img = requests.get(url_images, headers=headers, params=params_img, timeout=10)
                   if resp_img.status_code == 200:
                       images_data = resp_img.json()
                       images_list = images_data.get('images', [])
                except Exception as ex_img:
                    logger.warning(f"Erro ao buscar imagens dedicadas do imóvel {orulo_id}: {str(ex_img)}")

                # 2. Se vazio, tenta detail (fallback antigo)
                # MODIFICADO: Valida se a lista de imagens tem URLs
                fallback_images = []
                if not images_list:
                    try:
                       detail_url = f"{base_url}/buildings/{orulo_id}"
                       resp_detail = requests.get(detail_url, headers=headers, timeout=10)
                       if resp_detail.status_code == 200:
                           detail_data = resp_detail.json()
                           potential_images = detail_data.get('images', [])
                           
                           # Valida lista 'images'
                           if potential_images and isinstance(potential_images[0], dict):
                               sample = potential_images[0]
                               if sample.get('1024x1024') or sample.get('520x280') or sample.get('url') or sample.get('id'):
                                   fallback_images = potential_images
                           
                           # Se não achou imagens boas, tenta mockups
                           if not fallback_images:
                               fallback_images = detail_data.get('mockups', [])
                    except Exception as ex_detail:
                        logger.warning(f"Erro ao buscar detalhes do imóvel {orulo_id}: {str(ex_detail)}")
                
                if not images_list and fallback_images:
                    images_list = fallback_images

                # 3. Fallback final: default_image da listagem
                if not images_list:
                    default_img = building.get('default_image')
                    if default_img and isinstance(default_img, dict):
                         # Pega a maior disponível
                        url_img = default_img.get('1024x1024') or default_img.get('520x280') or default_img.get('200x140')
                        if url_img:
                            images_list.append({'url': url_img})

                # Processa as imagens encontradas (Limite aumentado para 25)
                for i, img_data in enumerate(images_list[:25]): 
                    # Se for string (url direta) ou dict
                    # A API de images retorna dict com várias resoluções. Pegar a maior.
                    img_url = None
                    if isinstance(img_data, str):
                        img_url = img_data
                    elif isinstance(img_data, dict):
                        img_url = img_data.get('1024x1024') or img_data.get('520x280') or img_data.get('url') # 'url' usado em mockups as vezes
                        # Fallback ID
                        if not img_url and img_data.get('id'):
                            img_url = f"https://static.orulo.com.br/images/properties/large/{img_data.get('id')}.jpg"
                    
                    if not img_url: continue
                    
                    try:
                        r = requests.get(img_url, timeout=10)
                        if r.status_code == 200:
                            clean_url = img_url.split('?')[0]
                            ext = clean_url.split('.')[-1]
                            if len(ext) > 4 or not ext: ext = 'jpg'
                            
                            filename = f"orulo_{imovel.id}_{i}.{ext}"
                            
                            imagem_obj = ImagemImovel(
                                imovel=imovel,
                                principal=(i == 0), 
                                ordem=i
                            )
                            imagem_obj.imagem.save(filename, ContentFile(r.content), save=True)
                            imported_images_count += 1
                    except Exception as e:
                        logger.warning(f"Erro ao baixar imagem {img_url}: {str(e)}")

                # --- Importar Plantas (Floor Plans) ---
                try:
                   url_plans = f"{base_url}/buildings/{orulo_id}/floor_plans"
                   params_plans = {'dimensions[]': '1024x1024'}
                   resp_plans = requests.get(url_plans, headers=headers, params=params_plans, timeout=10)
                   if resp_plans.status_code == 200:
                       plans_list = resp_plans.json().get('floor_plans', [])

                       # Prioriza o mesmo comportamento da sincronização unitária:
                       # plantas devem ir para ImagemUnidade quando houver match de área.
                       count_plans = associar_plantas_a_unidades(imovel, plans_list, max_plans=10)

                       # Fallback: se não houver associação, mantém planta no álbum geral do imóvel.
                       if count_plans == 0:
                           start_order = imported_images_count + 1
                           for j, plan in enumerate(plans_list[:5]):
                               plan_url = plan.get('1024x1024') or plan.get('520x280')
                               if not plan_url:
                                   continue
                               try:
                                   r_plan = requests.get(plan_url, timeout=10)
                                   if r_plan.status_code == 200:
                                       filename = f"orulo_plan_{imovel.id}_{j}.jpg"
                                       imagem_obj = ImagemImovel(
                                           imovel=imovel,
                                           principal=False,
                                           ordem=start_order + j
                                       )
                                       imagem_obj.imagem.save(filename, ContentFile(r_plan.content), save=True)
                               except Exception as e_plan:
                                   logger.warning(f"Erro ao baixar planta {plan_url}: {str(e_plan)}")

                except Exception as ex_plans:
                    logger.warning(f"Erro ao buscar plantas do imóvel {orulo_id}: {str(ex_plans)}")


                total_importados += 1

        except Exception as e:
            logger.exception(f"Erro crítico na página {page}")
            if progress_callback:
                progress_callback(100, f"Erro crítico: {str(e)}")
            return False, f"Erro durante importação na página {page}: {str(e)}", total_importados

    if progress_callback:
        progress_callback(100, "Concluído!")
        
    return True, "Importação concluída com sucesso.", total_importados

def sincronizar_imovel_orulo(imovel_id):
    """
    Sincroniza um único imóvel com a API da Órulo.
    Retorna: (sucesso, resultado_dict)
    """
    result = {
        'message': '',
        'changes': [],
        'removed': False
    }

    try:
        imovel = Imovel.objects.get(pk=imovel_id)
        if not imovel.is_orulo or not imovel.orulo_id:
            result['message'] = "Imóvel não possui vínculo válido com a Órulo."
            return False, result

        headers = get_orulo_auth_header()
        if not headers:
            result['message'] = "Falha na autenticação com a API."
            return False, result

        base_url = settings.ORULO_BASE_URL
        url = f"{base_url}/buildings/{imovel.orulo_id}"
        
        response = requests.get(url, headers=headers, timeout=10)

        # Se retorna 404/410, significa que foi removido
        if response.status_code in [404, 410]:
            if not imovel.removido_na_origem:
                imovel.removido_na_origem = True
                imovel.ativo = False
                imovel.save()
                result['changes'].append("Imóvel marcado como removido na origem.")
                result['changes'].append("Imóvel desativado.")
            else:
                result['changes'].append("Imóvel já estava marcado como removido.")
            
            result['removed'] = True
            result['message'] = "Imóvel não encontrado na Órulo."
            return True, result

        if response.status_code != 200:
            result['message'] = f"Erro na API ao sincronizar: {response.status_code}"
            return False, result

        # Se encontrou (200 OK)
        data = response.json()
        
        # Recuperação
        if imovel.removido_na_origem:
            imovel.removido_na_origem = False
            imovel.save()
            result['changes'].append("Imóvel recuperado (não está mais removido na origem).")

        # Atualiza status
        status_api = str(data.get('status', '')).lower()
        novo_status = 'EM_OBRA'
        if any(x in status_api for x in ['pronto', 'ready', 'used']):
            novo_status = 'PRONTO'
        
        if imovel.status != novo_status:
            result['changes'].append(f"Status atualizado de {imovel.status} para {novo_status}.")
            imovel.status = novo_status

        # --- NOVOS CAMPOS (Solicitados em 12/02/2026) ---
        # Garantir que developer_name seja atribuido corretamente
        developer_data = data.get('developer')
        if developer_data and isinstance(developer_data, dict):
             imovel.construtora = developer_data.get('name')
        
        # Datas com parser seguro
        imovel.data_lancamento = parse_orulo_date(data.get('launch_date') or data.get('launched_at'))
        imovel.data_entrega = parse_orulo_date(data.get('completion_date') or data.get('delivery_date') or data.get('delivered_at'))
        
        imovel.unidades_por_andar = data.get('units_per_floor')
        imovel.total_unidades = data.get('total_units') or data.get('units_count')
        imovel.numero_andares = data.get('floors') or data.get('floors_count')
        imovel.area_total = data.get('land_area') # Área do Terreno
        imovel.area_laje = data.get('standard_floor_area') # Área da Laje (se disponível)

        imovel.save()

        # --- A. Sincronizar Tipologias (Unidades) ---
        try:
            url_typologies = f"{base_url}/buildings/{imovel.orulo_id}/typologies"
            resp_typ = requests.get(url_typologies, headers=headers, params={'include[]': 'not_available'}, timeout=10)
            
            if resp_typ.status_code == 200:
                typologies = resp_typ.json().get('typologies', [])
                if typologies:
                    # Estratégia: Atualizar existentes por título ou criar novas
                    count_units_new = 0
                    min_price = None
                    for typ in typologies:
                         nome_unidade = f"{typ.get('type', 'Unidade')} - {typ.get('reference', '') or typ.get('id')}"
                         price = Decimal(typ.get('discount_price') or typ.get('original_price') or 0)
                         if price and price > 0:
                             if min_price is None or price < min_price:
                                 min_price = price
                         
                         unit_obj, created = Unidade.objects.update_or_create(
                             imovel=imovel,
                             titulo=nome_unidade,
                             defaults={
                                 'area_m2': int(typ.get('private_area') or typ.get('total_area') or 0),
                                 'quartos': int(typ.get('bedrooms', 0)),
                                 'banheiros': int(typ.get('bathrooms', 0)),
                                 'suites': int(typ.get('suites', 0)),
                                 'vagas': int(typ.get('parking', 0)),
                                 'ativo': True
                             }
                         )
                         if created: count_units_new += 1
                    
                    if count_units_new > 0:
                        result['changes'].append(f"{count_units_new} novas tipologias/unidades importadas.")
                    if min_price and (not imovel.preco or min_price != imovel.preco):
                        imovel.preco = min_price
                        imovel.save(update_fields=['preco'])
        except Exception as e_typ:
            logger.warning(f"Erro sync typologies: {str(e_typ)}")


        # --- B. Sincronizar Imagens (Com Fallback) ---
        try:
            images_list = []
            
            # 1. Tenta endpoint de imagens dedicado
            try:
                url_images = f"{base_url}/buildings/{imovel.orulo_id}/images"
                params_img = {'dimensions[]': '1024x1024'}
                resp_img = requests.get(url_images, headers=headers, params=params_img, timeout=10)
                if resp_img.status_code == 200:
                    images_list = resp_img.json().get('images', [])
            except Exception as ex_img:
                logger.warning(f"Erro ao buscar imagens dedicadas no sync: {str(ex_img)}")

            # 2. Fallback para dados locais (do detail response)
            # Verifica se 'images' tem dados válidos. 
            # Às vezes API retorna metadados (id, desc) mas não url. Nesse caso tentamos construir via ID.
            fallback_images = data.get('images', [])
            if fallback_images and isinstance(fallback_images[0], dict):
                 sample = fallback_images[0]
                 if not (sample.get('1024x1024') or sample.get('520x280') or sample.get('url') or sample.get('id')):
                     fallback_images = []
            
            if not images_list and fallback_images:
                images_list = fallback_images

            # 3. Fallback mockups
            if not images_list:
                images_list = data.get('mockups', [])

            # 4. Fallback final: default_image
            if not images_list:
                default_img = data.get('default_image')
                if default_img and isinstance(default_img, dict):
                     url_img = default_img.get('1024x1024') or default_img.get('520x280') or default_img.get('200x140')
                     if url_img:
                        images_list.append({'url': url_img})
            
            if images_list:
                # Remove imagens anteriores para garantir ordem e atualidade
                imovel.imagens.all().delete()
                
                count_img = 0
                for i, img_data in enumerate(images_list[:25]):
                    img_url = None
                    if isinstance(img_data, str):
                        img_url = img_data
                    elif isinstance(img_data, dict):
                        img_url = img_data.get('1024x1024') or img_data.get('520x280') or img_data.get('url')
                        # Fallback: Construir URL do ID
                        if not img_url and img_data.get('id'):
                            img_url = f"https://static.orulo.com.br/images/properties/large/{img_data.get('id')}.jpg"
                    
                    if not img_url: continue

                    try:
                        r = requests.get(img_url, timeout=10)
                        if r.status_code == 200:
                            clean_url = img_url.split('?')[0]
                            ext = clean_url.split('.')[-1]
                            if len(ext) > 4 or not ext: ext = 'jpg'
                            
                            filename = f"orulo_sync_{imovel.id}_{i}.{ext}"
                            imd = ImagemImovel(imovel=imovel, principal=(i==0), ordem=i)
                            imd.imagem.save(filename, ContentFile(r.content), save=True)
                            count_img += 1
                    except Exception as e:
                        pass
                
                if count_img > 0:
                    result['changes'].append(f"{count_img} imagens atualizadas do servidor.")
        except Exception as e_img:
            logger.warning(f"Erro sync imagens: {str(e_img)}")


        # --- C. Sincronizar Plantas ---
        try:
             url_plans = f"{base_url}/buildings/{imovel.orulo_id}/floor_plans"
             params_plans = {'dimensions[]': '1024x1024'}
             resp_plans = requests.get(url_plans, headers=headers, params=params_plans, timeout=10)
             if resp_plans.status_code == 200:
                 plans = resp_plans.json().get('floor_plans', [])
                 if plans:
                     count_plans = associar_plantas_a_unidades(imovel, plans, max_plans=10)
                     
                     if count_plans > 0:
                         result['changes'].append(f"{count_plans} plantas processadas e associadas a unidades.")
        except Exception as e_plan:
             logger.warning(f"Erro sync plantas: {str(e_plan)}")


        # --- D. Sincronizar Arquivos ---
        try:
             # Arquivos geralmente vêm no payload principal 'data' sob a chave 'files' ou 'attachments'
             # Se a chave 'files' existir no detail do imóvel:
             files_list = data.get('files', [])
             if files_list:
                 imovel.arquivos.all().delete() # Limpa anteriores para resync completo
                 count_files = 0
                 
                 for f_data in files_list:
                     file_id = f_data.get('id')
                     file_name = f_data.get('name') or f"arquivo_{file_id}"
                     file_type = f_data.get('type')
                     file_url = f_data.get('url')
                     
                     # Se não tiver URL mas tiver ID, busca detalhes
                     if not file_url and file_id:
                         try:
                             url_file_detail = f"{base_url}/buildings/{imovel.orulo_id}/files/{file_id}"
                             r_fd = requests.get(url_file_detail, headers=headers, timeout=10)
                             if r_fd.status_code == 200:
                                 file_detail = r_fd.json()
                                 file_url = file_detail.get('url')
                                 if not file_name or file_name.startswith('arquivo_'):
                                     file_name = file_detail.get('name')
                         except Exception as e_fd:
                             # logger.warning(f"Failed to fetch details for file {file_id}: {e_fd}")
                             pass

                     if not file_url: continue

                     try:
                         # Download content
                         r_down = requests.get(file_url, timeout=30)
                         if r_down.status_code == 200:
                             arq_obj = ArquivoImovel(
                                 imovel=imovel,
                                 nome=file_name,
                                 tipo=file_type or 'Outros'
                             )
                             # Determina extensão
                             ext = file_name.split('.')[-1] if '.' in file_name else 'pdf'
                             if len(ext) > 5: ext = 'pdf'
                             
                             arq_obj.arquivo.save(f"{file_id}.{ext}", ContentFile(r_down.content), save=True)
                             count_files += 1
                     except Exception as e_down:
                         # logger.warning(f"Error downloading file {file_url}: {e_down}")
                         pass
                 
                 if count_files > 0:
                     result['changes'].append(f"{count_files} arquivos documentais baixados.")
        except Exception as e_files:
             logger.warning(f"Erro sync arquivos: {str(e_files)}")
        if not result['changes']:
            result['changes'].append("Nenhuma alteração detectada nos dados básicos.")

        imovel.save()
        result['message'] = "Sincronização completa realizada."
        return True, result

    except Imovel.DoesNotExist:
        result['message'] = "Imóvel não encontrado localmente."
        return False, result
    except Exception as e:
        logger.error(f"Erro ao sincronizar imóvel {imovel_id}: {str(e)}")
        result['message'] = f"Erro interno: {str(e)}"
        return False, result
