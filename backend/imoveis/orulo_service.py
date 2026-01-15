import requests
import os
from .models import Imovel
from django.conf import settings

def importar_imoveis_orulo():
    """
    Função auxiliar para importar imóveis da API da Órulo.
    Retorna uma tupla: (sucesso: bool, mensagem: str, total_importados: int)
    """
    # Configuração - Idealmente use variáveis de ambiente
    ORULO_TOKEN = os.getenv('ORULO_TOKEN')
    URL_API = "https://www.orulo.com.br/api/v2/buildings" 
    
    if not ORULO_TOKEN:
        return False, "Token da Órulo não configurado (.env).", 0

    headers = {
        "Authorization": f"Bearer {ORULO_TOKEN}"
    }

    try:
        # Exemplo simples: busca página 1
        response = requests.get(f"{URL_API}?page=1", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            buildings = data.get('buildings', [])
            
            count_created = 0
            
            for item in buildings:
                nome_imovel = item.get('name')
                
                # Verifica duplicidade simples pelo nome
                if Imovel.objects.filter(titulo=nome_imovel).exists():
                    continue

                # Mapeamento Básico
                Imovel.objects.create(
                    titulo=nome_imovel,
                    descricao=item.get('description', '')[:500] if item.get('description') else "Sem descrição",
                    rua=item.get('address', {}).get('street'),
                    numero=item.get('address', {}).get('number'),
                    bairro_oficial=item.get('address', {}).get('area'),
                    cidade=item.get('address', {}).get('city'),
                    uf=item.get('address', {}).get('state'),
                    
                    # Valores seguros (get com default)
                    area=item.get('min_area', 0), 
                    quartos=item.get('min_bedrooms', 0),
                    banheiros=item.get('min_bathrooms', 0),
                    vagas=item.get('min_parking', 0),
                    preco=item.get('min_price', 0),
                    
                    tipo='apartamento', 
                    finalidade='venda'
                )
                count_created += 1

            return True, f"Importação finalizada com sucesso.", count_created
        else:
            return False, f"Erro da API: {response.status_code}", 0

    except Exception as e:
        return False, f"Erro na conexão: {str(e)}", 0
