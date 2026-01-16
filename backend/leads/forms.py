from django import forms
from .models import Acompanhamento

class AcompanhamentoForm(forms.ModelForm):
    class Meta:
        model = Acompanhamento
        fields = ['texto', 'proximo_passo', 'data_proximo_contato']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva o contato...'}),
            'proximo_passo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ligar semana que vem'}),
            'data_proximo_contato': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
