from django.db import models
from imoveis.models import Imovel

class Lead(models.Model):
    TIPO_CONTATO_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telefone', 'Ligação'),
    ]

    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    tipo_contato = models.CharField(max_length=10, choices=TIPO_CONTATO_CHOICES, default='whatsapp', verbose_name='Preferência de Contato')
    
    # O imóvel é opcional, caso o lead venha de uma página institucional, mas no fluxo atual virá do detalhe
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    
    mensagem = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    atendido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        return f"{self.nome} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"


class Acompanhamento(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='acompanhamentos')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')
    texto = models.TextField(verbose_name='Acompanhamento')
    
    # Ideias para enriquecer
    proximo_passo = models.CharField(max_length=200, blank=True, null=True, verbose_name='Próximo Passo')
    data_proximo_contato = models.DateField(blank=True, null=True, verbose_name='Data do Próximo Contato')
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Acompanhamento'
        verbose_name_plural = 'Acompanhamentos'

    def __str__(self):
        return f"Acompanhamento de {self.lead.nome} em {self.data_hora.strftime('%d/%m/%Y')}"
