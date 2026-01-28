from rest_framework import serializers
from .models import Imovel, ImagemImovel

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ('id', 'imagem', 'principal', 'ordem')

class ImovelSerializer(serializers.ModelSerializer):
    imagens = ImagemImovelSerializer(many=True, read_only=True)
    imagem_principal = serializers.SerializerMethodField()
    class Meta:
            model = Imovel
            fields = (
                'id',
                'titulo',
                'descricao',
                'preco',
                'preco_m2',
                'condominio',
                'iptu',
                'parcela',
                'tipo',
                'bairro',
                'cidade',
                'imagens',
                'imagem_principal',
            )

    def get_imagem_principal(self, obj):
        imagem = obj.imagens.filter(principal=True).first()
        return imagem.imagem.url if imagem else None
