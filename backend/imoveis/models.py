from django.db import models
from django.utils.text import slugify

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
    ]

    titulo = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField()
    instalacoes = models.ManyToManyField(Instalacao, blank=True, related_name="imoveis")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    bairro = models.CharField(max_length=100, verbose_name="Bairro (Comercial)")
    bairro_oficial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro (Oficial)", help_text="Bairro de registro (ex: Cidade Monções)")
    cidade = models.CharField(max_length=100, default='São Paulo')
    uf = models.CharField(max_length=2, default='SP', verbose_name="UF")
    rua = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=True, null=True)

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
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
    imovel = models.ForeignKey(
        Imovel,
        related_name='unidades',
        on_delete=models.CASCADE
    )

    titulo = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=12, decimal_places=2)

    area_m2 = models.PositiveIntegerField()
    quartos = models.PositiveIntegerField()
    banheiros = models.PositiveIntegerField()
    suites = models.PositiveIntegerField()
    vagas = models.PositiveIntegerField()

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
    imagem = models.ImageField(upload_to='imoveis/')
    principal = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

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
    imagem = models.ImageField(upload_to='unidades/')
    principal = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
            verbose_name = 'Imagem da Unidade'
            verbose_name_plural = 'Imagens das Unidades'
            ordering = ['ordem']

    def __str__(self):
        return f"Imagem da unidade {self.unidade.titulo}"
