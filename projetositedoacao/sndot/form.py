from django import forms
from .models import Doador, Receptor, Administrador
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
# Estados e cidades do Brasil
BRAZILIAN_STATES_AND_CITIES = {
    "AC": ["Rio Branco", "Cruzeiro do Sul"],
    "AL": ["Maceió", "Arapiraca"],
    "AM": ["Manaus", "Parintins"],
    "AP": ["Macapá", "Santana"],
    "BA": ["Salvador", "Feira de Santana"],
    "CE": ["Fortaleza", "Caucaia"],
    "DF": ["Brasília"],
    "ES": ["Vitória", "Vila Velha"],
    "GO": ["Goiânia", "Aparecida de Goiânia", "Anápolis"],
    "MA": ["São Luís", "Imperatriz"],
    "MG": ["Belo Horizonte", "Uberlândia", "Contagem"],
    "MS": ["Campo Grande", "Dourados"],
    "MT": ["Cuiabá", "Várzea Grande"],
    "PA": ["Belém", "Ananindeua"],
    "PB": ["João Pessoa", "Campina Grande"],
    "PE": ["Recife", "Jaboatão dos Guararapes"],
    "PI": ["Teresina", "Parnaíba"],
    "PR": ["Curitiba", "Londrina", "Maringá"],
    "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias"],
    "RN": ["Natal", "Mossoró"],
    "RO": ["Porto Velho", "Ji-Paraná"],
    "RR": ["Boa Vista"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Canoas"],
    "SC": ["Florianópolis", "Joinville", "Blumenau"],
    "SE": ["Aracaju", "Nossa Senhora do Socorro"],
    "SP": ["São Paulo", "Campinas", "Guarulhos", "São Bernardo do Campo"],
    "TO": ["Palmas", "Araguaína"]
}

STATE_CHOICES = [('', 'Selecione o Estado')] + [(uf, uf) for uf in sorted(BRAZILIAN_STATES_AND_CITIES.keys())]

SEXO_CHOICES = [
    ('', 'Selecione'),
    ('M', 'Masculino'),
    ('F', 'Feminino')
]

TIPO_SANGUINEO_CHOICES = [
    ('', 'Selecione'),
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

PROFISSAO_CHOICES = [
    ('', 'Selecione'),
    ('Engenheiro', 'Engenheiro'),
    ('Médico', 'Médico'),
    ('Professor', 'Professor'),
    ('Estudante', 'Estudante'),
    ('Aposentado', 'Aposentado'),
    ('Outra', 'Outra')
]

ESTADO_CIVIL_CHOICES = [
    ('', 'Selecione'),
    ('Solteiro', 'Solteiro'),
    ('Solteira', 'Solteira'),
    ('Casado', 'Casado'),
    ('Casada', 'Casada'),
    ('Divorciado', 'Divorciado'),
    ('Divorciada', 'Divorciada'),
    ('Viúvo', 'Viúvo'),
    ('Viúva', 'Viúva'),
    ('União Estável', 'União Estável')
]

class ImportarDoadoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class CadastrarDoadorForm(forms.ModelForm):
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")

    class Meta:
        model = Doador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        # Remove pontos e traço
        cpf_numeros = re.sub(r'[.-]', '', cpf or '')

        # Verifica se tem exatamente 11 dígitos numéricos
        if not re.fullmatch(r'\d{11}', cpf_numeros):
            raise ValidationError('CPF deve estar no formato 000.000.000-00 ou conter 11 dígitos numéricos.')

        # Verifica unicidade no modelo Doador
        if Doador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como doador.')

        # Opcional: verificar se já existe como receptor
        if Receptor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como receptor.')

        # Retorna o CPF normalizado (sem pontuação)
        return cpf_numeros
    
    def clean(self):
        dados_validados = super().clean()
        profissao = dados_validados.get('profissao')
        outra_profissao = dados_validados.get('outra_profissao')
        sexo = dados_validados.get('sexo')
        estado_civil = dados_validados.get('estado_civil')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            dados_validados['profissao'] = outra_profissao

        if dados_validados.get('estado_natal') and not dados_validados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados_validados.get('estado_residencia') and not dados_validados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino_estados = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino_estados = ['Solteira', 'Casada', 'Divorciada', 'Viúva']
        if sexo == 'M' and estado_civil in feminino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        return dados_validados


class ImportarReceptoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

class CadastrarReceptorForm(forms.ModelForm):
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")
    
    class Meta:
        model = Receptor
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia',
            'orgao_necessario', 'gravidade_condicao', 'centro_transplante', 'posicao_lista_espera'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        cpf_numeros = re.sub(r'[.-]', '', cpf or '')

        if not re.fullmatch(r'\d{11}', cpf_numeros):
            raise ValidationError('CPF deve estar no formato 000.000.000-00 ou conter 11 dígitos numéricos.')

        if Receptor.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como receptor.')

        # Opcional: verificar se já existe como doador
        if Doador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como doador.')

        return cpf_numeros

    def clean(self):
        dados_validados = super().clean()
        profissao = dados_validados.get('profissao')
        outra_profissao = dados_validados.get('outra_profissao')
        sexo = dados_validados.get('sexo')
        estado_civil = dados_validados.get('estado_civil')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra' and outra_profissao:
            dados_validados['profissao'] = outra_profissao

        if dados_validados.get('estado_natal') and not dados_validados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados_validados.get('estado_residencia') and not dados_validados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino_estados = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino_estados = ['Solteira', 'Casada', 'Divorciada', 'Viúva']
        if sexo == 'M' and estado_civil in feminino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        return dados_validados

class CadastrarAdministradorForm(forms.ModelForm):
    estado_natal = forms.ChoiceField(choices=STATE_CHOICES, label="Estado Natal")
    estado_residencia = forms.ChoiceField(choices=STATE_CHOICES, label="Estado de Residência")
    cidade_natal = forms.CharField(max_length=100, required=False, label="Cidade Natal")
    cidade_residencia = forms.CharField(max_length=100, required=False, label="Cidade de Residência")
    outra_profissao = forms.CharField(max_length=100, required=False)
    sexo = forms.ChoiceField(choices=SEXO_CHOICES, label="Sexo")
    tipo_sanguineo = forms.ChoiceField(choices=TIPO_SANGUINEO_CHOICES, label="Tipo Sanguíneo")
    profissao = forms.ChoiceField(choices=PROFISSAO_CHOICES, label="Profissão")
    estado_civil = forms.ChoiceField(choices=ESTADO_CIVIL_CHOICES, label="Estado Civil")

    senha = forms.CharField(widget=forms.PasswordInput(), label="Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(), label="Confirmar Senha")

    class Meta:
        model = Administrador
        fields = [
            'cpf', 'nome', 'tipo_sanguineo', 'data_nascimento', 'sexo',
            'profissao', 'estado_natal', 'cidade_natal', 'estado_residencia',
            'cidade_residencia', 'estado_civil', 'contato_emergencia',
            'nome_usuario', 'senha'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
        }
        input_formats = {'data_nascimento': ['%Y/%m/%d', '%Y-%m-%d']}

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf_numeros = re.sub(r'[.-]', '', cpf or '')

        if not re.fullmatch(r'\d{11}', cpf_numeros):
            raise ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')

        if Administrador.objects.filter(cpf=cpf_numeros).exists():
            raise ValidationError('Este CPF já está cadastrado como administrador.')

        return cpf_numeros

    def clean(self):
        dados = super().clean()
        profissao = dados.get('profissao')
        outra_profissao = dados.get('outra_profissao')
        sexo = dados.get('sexo')
        estado_civil = dados.get('estado_civil')
        senha = dados.get('senha')
        confirmar_senha = dados.get('confirmar_senha')

        if profissao == 'Outra' and not outra_profissao:
            self.add_error('outra_profissao', 'Por favor, especifique a outra profissão.')
        elif profissao == 'Outra':
            dados['profissao'] = outra_profissao

        if dados.get('estado_natal') and not dados.get('cidade_natal'):
            self.add_error('cidade_natal', 'Cidade natal é obrigatória quando o estado é selecionado.')

        if dados.get('estado_residencia') and not dados.get('cidade_residencia'):
            self.add_error('cidade_residencia', 'Cidade de residência é obrigatória quando o estado é selecionado.')

        masculino_estados = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
        feminino_estados = ['Solteira', 'Casada', 'Divorciada', 'Viúva']
        if sexo == 'M' and estado_civil in feminino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo masculino.')
        elif sexo == 'F' and estado_civil in masculino_estados:
            self.add_error('estado_civil', 'Estado civil selecionado não corresponde ao sexo feminino.')

        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')

        return dados

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Criptografar a senha
        senha = self.cleaned_data.get('senha')
        if senha:
            instance.senha = make_password(senha)

        if commit:
            instance.save()
        return instance

class ImportarAdministradoresForm(forms.Form):
    json_file = forms.FileField(
        label='Arquivo JSON',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )
