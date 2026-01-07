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
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default='São Paulo')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    ativo = models.BooleanField(default=True)

    imagem_principal = models.ImageField(
        upload_to='imoveis/',
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.bairro}'
