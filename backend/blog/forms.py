from django import forms
from .models import Post, Propaganda

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'categoria', 'status', 'imagem_capa', 'is_featured', 'conteudo', 'data_publicacao', 'meta_title', 'meta_description']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'imagem_capa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_publicacao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
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
