from django.urls import path
from .views import ImovelListAPIView, ImovelDetailAPIView

urlpatterns = [
    path('imoveis/', ImovelListAPIView.as_view()),
    path('imoveis/<int:pk>/', ImovelDetailAPIView.as_view()),
]
