from django import forms
from .models import Post, Propaganda

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'conteudo', 'imagem_capa', 'ativo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'imagem_capa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class PropagandaForm(forms.ModelForm):
    class Meta:
        model = Propaganda
        fields = ['titulo', 'imagem', 'link_destino', 'ativo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link_destino': forms.URLInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
