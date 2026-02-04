from django.db import models
from django.utils.text import slugify
from datetime import date
import os
import random

def get_imovel_upload_path(instance, filename):
    """
    Gera o caminho: imoveis/<slug_do_imovel>/<nome_arquivo>
    """
    return os.path.join('imoveis', instance.imovel.slug, filename)

def get_unidade_upload_path(instance, filename):
    """
    Gera o caminho: imoveis/<slug_do_imovel>/unidades/<nome_arquivo>
    """
    return os.path.join('imoveis', instance.unidade.imovel.slug, 'unidades', filename)

class Instalacao(models.Model):
    nome = models.CharField(max_length=100)
    # Opcional: adicionar um campo para ícone (ex: FontAwesome)
    icone = models.CharField(max_length=50, blank=True, null=True, help_text="Classe do FontAwesome (ex: fas fa-swimming-pool)")

    class Meta:
        verbose_name = "Instalação"
        verbose_name_plural = "Instalações"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Imovel(models.Model):
    TIPO_CHOICES = [
        ('MCMV', 'Minha Casa Minha Vida'),
        ('MEDIO', 'Médio Padrão'),
        ('ALTO', 'Alto Padrão'),
        ('LOTEAMENTO', 'Loteamento'),
        ('HARAS', 'Haras / Rural'),
    ]

    STATUS_CHOICES = [
        ('EM_OBRA', 'Em Construção'),
        ('PRONTO', 'Pronto'),
        ('LANCAMENTO', 'Lançamento'),
    ]

    titulo = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    descricao = models.TextField()
    instalacoes = models.ManyToManyField(Instalacao, blank=True, related_name="imoveis")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PLANTA', 
        verbose_name="Status da Obra"
    )
    destaque = models.BooleanField(default=False, verbose_name="Destaque", help_text="Exibe este imóvel com destaque na Home e nas buscas")
    preco = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Preço")
    preco_m2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Preço do m²")
    condominio = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Condomínio")
    iptu = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="IPTU")
    parcela = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Parcela")
    
    # Adicionar campo para área total do terreno
    area_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Área Total do Terreno"
    )

    bairro = models.CharField(max_length=100, verbose_name="Bairro (Comercial)")
    bairro_oficial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro (Oficial)", help_text="Bairro de registro (ex: Cidade Monções)")
    cidade = models.CharField(max_length=100, default='São Paulo')
    uf = models.CharField(max_length=2, default='SP', verbose_name="UF")
    rua = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Geolocalização
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Campos de Controle Interno
    data_lancamento = models.DateField(blank=True, null=True, verbose_name="Data de Lançamento")
    unidades_por_andar = models.PositiveIntegerField(blank=True, null=True, verbose_name="Unidades por Andar")
    data_entrega = models.DateField(blank=True, null=True, verbose_name="Data de Entrega")
    total_unidades = models.PositiveIntegerField(blank=True, null=True, verbose_name="Total de Unidades")
    numero_andares = models.PositiveIntegerField(blank=True, null=True, verbose_name="Número de Andares")
    area_laje = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Área da Laje")
    construtora = models.CharField(max_length=255, blank=True, null=True, verbose_name="Construtora")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # Integração Orulo
    orulo_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="ID Órulo")
    is_orulo = models.BooleanField(default=False, verbose_name="Importado da Órulo")
    removido_na_origem = models.BooleanField(default=False, verbose_name="Removido na Órulo")

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.data_entrega and self.data_entrega <= date.today():
             self.status = 'PRONTO'

        if not self.slug:
            base_slug = slugify(f"{self.titulo}-{self.bairro}")
            slug = base_slug
            contador = 1

            while Imovel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'

    def __str__(self):
        return f'{self.titulo} - {self.bairro}'

class Unidade(models.Model):
    TITULO_CHOICES = [
        ('Apartamento', 'Apartamento'),
        ('Cobertura', 'Cobertura'),
        ('Lote', 'Lote'),
    ]

    imovel = models.ForeignKey(
        Imovel,
        related_name='unidades',
        on_delete=models.CASCADE
    )

    titulo = models.CharField(max_length=255, choices=TITULO_CHOICES, default='Apartamento')

    area_m2 = models.PositiveIntegerField()
    quartos = models.PositiveIntegerField(default=0, blank=True, null=True)
    banheiros = models.PositiveIntegerField(default=0, blank=True, null=True)
    suites = models.PositiveIntegerField(default=0, blank=True, null=True)
    vagas = models.PositiveIntegerField(default=0, blank=True, null=True)

    ativo = models.BooleanField(default=True)  

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return f"{self.titulo} ({self.imovel.titulo})"

class ImagemImovel(models.Model):
    imovel = models.ForeignKey(
        Imovel,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to=get_imovel_upload_path)
    principal = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.ordem == 0:
            self.ordem = random.randint(1, 1000)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Imagem do Imóvel'
        verbose_name_plural = 'Imagens dos Imóveis'
        ordering = ['-principal', 'ordem']

    def __str__(self):
        return f"Imagem do imóvel {self.imovel.titulo}"

class ImagemUnidade(models.Model):
    unidade = models.ForeignKey(
        Unidade,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to=get_unidade_upload_path)
    principal = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.ordem == 0:
            self.ordem = random.randint(1, 1000)
        super().save(*args, **kwargs)

    class Meta:
            verbose_name = 'Imagem da Unidade'
            verbose_name_plural = 'Imagens das Unidades'
            ordering = ['ordem']

    def __str__(self):
        return f"Imagem da unidade {self.unidade.titulo}"

def get_arquivo_upload_path(instance, filename):
    return os.path.join('imoveis', instance.imovel.slug, 'arquivos', filename)

class ArquivoImovel(models.Model):
    imovel = models.ForeignKey(
        Imovel,
        related_name='arquivos',
        on_delete=models.CASCADE
    )
    arquivo = models.FileField(upload_to=get_arquivo_upload_path)
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True, null=True) # Ex: Tabela, Memorial
    orulo_id = models.CharField(max_length=50, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Arquivo do Imóvel'
        verbose_name_plural = 'Arquivos dos Imóveis'

    def __str__(self):
        return self.nome
