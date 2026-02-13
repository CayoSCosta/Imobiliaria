from django import forms
from .models import Imovel, ImagemImovel, Unidade, Instalacao

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ImovelImagensForm(forms.Form):
    imagens = MultipleFileField(
        label='Selecione as imagens',
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagens'].widget.attrs['class'] = 'form-control'

class ImovelArquivosForm(forms.Form):
    arquivos = MultipleFileField(
        label='Selecione os arquivos',
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['arquivos'].widget.attrs['class'] = 'form-control'

class UnidadeForm(forms.ModelForm):
    imagem_planta = forms.ImageField(label="Imagem da Planta", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'ativo' in field_name:
                 field.widget.attrs['class'] = 'form-check-input'
            else:
                 field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Unidade
        exclude = ['imovel', 'criado_em']
        labels = {
            'titulo': 'Título da Unidade',
            'area_m2': 'Área (m²)',
            'quartos': 'Quartos',
            'banheiros': 'Banheiros',
            'suites': 'Suítes',
            'vagas': 'Vagas',
            'ativo': 'Ativo?'
        }

class ImovelInstalacoesForm(forms.ModelForm):
    class Meta:
        model = Imovel
        fields = ['instalacoes']
        widgets = {
            'instalacoes': forms.CheckboxSelectMultiple
        }
        labels = {
            'instalacoes': "Selecione as Instalações Disponíveis"
        }

class InstalacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Instalacao
        fields = ['nome', 'icone']
        labels = {
            'nome': 'Nome da Instalação',
            'icone': 'Ícone (FontAwesome class)'
        }
        help_texts = {
            'icone': 'Ex: fas fa-swimming-pool'
        }

class ImovelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Imovel
        fields = [
            'titulo', 'descricao', 'tipo', 'status', 'destaque', 'destaque_blog',
            'preco', 'preco_m2', 'condominio', 'iptu', 'parcela', 
            'rua', 'numero', 'bairro', 'bairro_oficial', 'cidade', 'uf', 'cep',
            'ativo',
            # Novos campos de controle
            'data_lancamento', 'unidades_por_andar', 'data_entrega', 
            'total_unidades', 'numero_andares', 'area_laje', 'area_total', 'construtora'
        ]
        labels = {
            'titulo': 'Título do Empreendimento',
            'descricao': 'Descrição',
            'tipo': 'Tipo',
            'status': 'Status da Obra',
            'destaque': 'Destaque?',
            'destaque_blog': 'Destaque no Blog?',
            'preco': 'Preço (R$)',
            'preco_m2': 'Preço do m² (R$)',
            'condominio': 'Condomínio (R$)',
            'iptu': 'IPTU (R$)',
            'parcela': 'Parcela (R$)',
            'rua': 'Endereço (Rua/Av)',
            'numero': 'Número',
            'bairro': 'Bairro Comercial',
            'bairro_oficial': 'Bairro Oficial',
            'cidade': 'Cidade',
            'uf': 'UF',
            'cep': 'CEP',
            'ativo': 'Ativo?',
            # Labels novos campos
            'data_lancamento': 'Data de Lançamento',
            'unidades_por_andar': 'Unidades por Andar',
            'data_entrega': 'Data de Entrega',
            'total_unidades': 'Total de Unidades',
            'numero_andares': 'Número de Andares',
            'area_laje': 'Área da Laje (m²)',
            'area_total': 'Área Total do Terreno (m²)',
            'construtora': 'Construtora',
        }
        widgets = {
             'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'}),
             'destaque': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'}),
             'destaque_blog': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'}),
             'descricao': forms.Textarea(attrs={'rows': 3}),
             'data_lancamento': forms.DateInput(attrs={'type': 'date'}),
             'data_entrega': forms.DateInput(attrs={'type': 'date'}),
        }
