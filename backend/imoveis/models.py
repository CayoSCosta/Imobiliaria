from django.db import models


class Imovel(models.Model):

    TIPO_CHOICES = [
        ('MCMV', 'Minha Casa Minha Vida'),
        ('MEDIO', 'Médio Padrão'),
        ('ALTO', 'Alto Padrão'),
    ]

    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=12, decimal_places=2)

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default='São Paulo')

    area_m2 = models.PositiveIntegerField(default=0)
    quartos = models.PositiveIntegerField(default=0)
    banheiros = models.PositiveIntegerField(default=0)
    suites = models.PositiveIntegerField(default=0)
    vagas = models.PositiveIntegerField(default=0)

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.bairro}'


class ImagemImovel(models.Model):
    imovel = models.ForeignKey(
        Imovel,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to='imoveis/')
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagem de {self.imovel.titulo}"
