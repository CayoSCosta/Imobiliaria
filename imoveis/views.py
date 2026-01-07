from rest_framework import generics
from .models import Imovel
from .serializers import ImovelSerializer

class ImovelListAPIView(generics.ListAPIView):
    serializer_class = ImovelSerializer

    def get_queryset(self):
        queryset = Imovel.objects.filter(ativo=True)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class ImovelDetailAPIView(generics.RetrieveAPIView):
    queryset = Imovel.objects.filter(ativo=True)
    serializer_class = ImovelSerializer
