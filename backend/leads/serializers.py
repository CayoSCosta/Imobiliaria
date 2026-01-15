from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'nome', 'telefone', 'tipo_contato', 'imovel', 'mensagem', 'data_criacao']
        read_only_fields = ['id', 'data_criacao']
