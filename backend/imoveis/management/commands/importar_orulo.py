from django.core.management.base import BaseCommand
import requests
import os
from imoveis.models import Imovel, ImagemImovel
from django.core.files.base import ContentFile
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Importa imóveis da API pública da Órulo'

    def handle(self, *args, **options):
        # Configuração - Idealmente use variáveis de ambiente
        ORULO_TOKEN = os.getenv('ORULO_TOKEN', 'seu_token_aqui')
        # URL de exemplo (verifique a doc oficial da Órulo para o endpoint correto de listagem)
        URL_API = "https://www.orulo.com.br/api/v2/buildings" 
        
        headers = {
            "Authorization": f"Bearer {ORULO_TOKEN}"
        }

        self.stdout.write("Iniciando importação...")

        try:
            # Exemplo de paginação simples (página 1)
            response = requests.get(f"{URL_API}?page=1", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                buildings = data.get('buildings', [])
                
                if not buildings:
                     self.stdout.write(self.style.WARNING("Nenhum imóvel encontrado na resposta."))

                for item in buildings:
                    # Mapeamento Básico (Adapte conforme o JSON real da Órulo)
                    nome_imovel = item.get('name')
                    ref_externa = item.get('id') # ID da Órulo
                    
                    # Evita duplicidade baseado em algum campo único ou slug
                    if Imovel.objects.filter(titulo=nome_imovel).exists():
                         self.stdout.write(f"Imóvel '{nome_imovel}' já existe. Pulando.")
                         continue

                    # Criação do Objeto Imóvel
                    # ATENÇÃO: Você precisará adaptar os campos abaixo para bater com o seu Model Imovel
                    novo_imovel = Imovel(
                        titulo=nome_imovel,
                        descricao=item.get('description', '')[:500], # Limite conforme seu model
                        rua=item.get('address', {}).get('street'),
                        numero=item.get('address', {}).get('number'),
                        bairro_oficial=item.get('address', {}).get('area'),
                        cidade=item.get('address', {}).get('city'),
                        uf=item.get('address', {}).get('state'),
                        
                        # Valores fictícios ou extraídos do JSON complexo da Órulo
                        area=item.get('min_area', 0), 
                        quartos=item.get('min_bedrooms', 0),
                        banheiros=item.get('min_bathrooms', 0),
                        vagas=item.get('min_parking', 0),
                        preco=item.get('min_price', 0),
                        
                        tipo='apartamento', # Default ou mapear do JSON
                        finalidade='venda'
                    )
                    novo_imovel.save()
                    self.stdout.write(self.style.SUCCESS(f"Imóvel criado: {novo_imovel.titulo}"))

                    # Importação de Imagens (Opcional - Exemplo)
                    # images = item.get('images', [])
                    # for img_url in images[:3]: # Pega as 3 primeiras
                    #     r_img = requests.get(img_url)
                    #     if r_img.status_code == 200:
                    #         img_temp = ContentFile(r_img.content)
                    #         img_name = f"orulo_{ref_externa}_{slugify(nome_imovel)}.jpg"
                    #         ImagemImovel.objects.create(imovel=novo_imovel, imagem=img_temp)

            else:
                self.stdout.write(self.style.ERROR(f"Erro na API: {response.status_code} - {response.text}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro crítico: {str(e)}"))
