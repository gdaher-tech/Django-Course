from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .form import (
    ImportarDoadoresForm, CadastrarDoadorForm,
    ImportarReceptoresForm, CadastrarReceptorForm
)
from .models import Doador, Receptor
from datetime import datetime
import json
from .models import Administrador
from .form import CadastrarAdministradorForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Orgao, CentroDistribuicao
from django.contrib.auth.decorators import login_required
from .models import Orgao, CentroDistribuicao
from django.contrib.auth.decorators import login_required

# --- Página Inicial ---
def home(request):
    return render(request, 'home.html')

def pagina_do_doador(request):
    return render(request, 'pagina_do_doador.html')

def pagina_do_receptor(request):
    return render(request, 'pagina_do_receptor.html')

def pagina_do_administrador(request):
    return render(request, 'pagina_do_administrador.html')

def index(request):
    return render(request, 'index.html')

# --- DOADOR ---

def importar_doadores(request):
    if request.method == 'POST':
        form = ImportarDoadoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                data = json.load(json_file)

                for item in data:
                    dados = item['dados']
                    dados.pop('id', None)  # Remove ID

                    # Converte a data
                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()

                    # Calcula idade
                    nascimento = dados['data_nascimento']
                    hoje = datetime.today().date()
                    idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

                    # Cria doador
                    Doador.objects.create(**dados)

                messages.success(request, "Doadores importados com sucesso.")
                return redirect('listar_doadores')
            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarDoadoresForm()
    return render(request, 'importar_doador.html', {'form': form})

@login_required
def cadastrar_doador(request):
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador cadastrado com sucesso.")
            return redirect('listar_doadores')
    else:
        form = CadastrarDoadorForm()
    return render(request, 'cadastrar_doador.html', {'form': form})


from django.core.paginator import Paginator

def listar_doadores(request):
    cpf = request.GET.get('cpf')
    doadores = Doador.objects.all()

    if cpf:
        doadores = doadores.filter(cpf__icontains=cpf)

    paginator = Paginator(doadores, 10)  # 10 doadores por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listar_doador.html', {'page_obj': page_obj, 'cpf': cpf})



def editar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        form = CadastrarDoadorForm(request.POST, instance=doador)
        if form.is_valid():
            form.save()
            messages.success(request, "Doador atualizado com sucesso.")
            return redirect('listar_doadores')
    else:
        form = CadastrarDoadorForm(instance=doador)
    return render(request, 'editar_doador.html', {'form': form})


def deletar_doador(request, pk):
    doador = get_object_or_404(Doador, pk=pk)
    if request.method == 'POST':
        doador.delete()
        messages.success(request, "Doador excluído com sucesso.")
        return redirect('listar_doadores')
    return render(request, 'deletar_doador.html', {'doador': doador})

# --- RECEPTOR ---
def importar_receptores(request):
    if request.method == 'POST':
        form = ImportarReceptoresForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                data = json.load(json_file)

                for item in data:
                    dados = item['dados']
                    dados.pop('id', None)

                    # Converte data
                    nascimento_str = dados.get('data_nascimento')
                    if nascimento_str:
                        dados['data_nascimento'] = datetime.strptime(nascimento_str, '%Y/%m/%d').date()

                    # Força campos que devem ser string
                    campos_char = [
                        'cidade_natal', 'estado_natal',
                        'cidade_residencia', 'estado_residencia',
                        'posicao_lista_espera', 'orgao_necessario',
                        'gravidade_condicao', 'centro_transplante',
                        'estado_civil', 'profissao', 'sexo', 'tipo_sanguineo',
                        'contato_emergencia'
                    ]
                    for campo in campos_char:
                        if campo in dados and dados[campo] is not None:
                            dados[campo] = str(dados[campo]).strip()

                    Receptor.objects.create(**dados)

                messages.success(request, "Receptores importados com sucesso.")
                return redirect('listar_receptores')

            except Exception as e:
                messages.error(request, f"Erro ao importar: {str(e)}")
    else:
        form = ImportarReceptoresForm()
    return render(request, 'importar_receptores.html', {'form': form})

@login_required
def cadastrar_receptor(request):
    if request.method == 'POST':
        form = CadastrarReceptorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Receptor cadastrado com sucesso.")
            return redirect('listar_receptores')
    else:
        form = CadastrarReceptorForm()
    return render(request, 'cadastrar_receptores.html', {'form': form})




def listar_receptores(request):
    cpf = request.GET.get('cpf')
    receptores = Receptor.objects.all()

    if cpf:
        receptores = receptores.filter(cpf__icontains=cpf)

    paginator = Paginator(receptores, 10)  # Mostra 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listar_receptores.html', {
        'page_obj': page_obj,
        'cpf': cpf,
    })



def editar_receptor(request, pk):
    receptor = get_object_or_404(Receptor, pk=pk)
    if request.method == 'POST':
        form = CadastrarReceptorForm(request.POST, instance=receptor)
        if form.is_valid():
            form.save()
            messages.success(request, "Receptor atualizado com sucesso.")
            return redirect('listar_receptores')
    else:
        form = CadastrarReceptorForm(instance=receptor)
    return render(request, 'editar_receptores.html', {'form': form})


def deletar_receptor(request, pk):
    receptor = get_object_or_404(Receptor, pk=pk)
    if request.method == 'POST':
        receptor.delete()
        messages.success(request, "Receptor excluído com sucesso.")
        return redirect('listar_receptores')
    return render(request, 'deletar_receptores.html', {'receptor': receptor})

# --- ADMINISTRADOR ---

def cadastrar_administrador(request):
    if request.method == 'POST':
        form = CadastrarAdministradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Administrador cadastrado com sucesso.")
            return redirect('listar_administradores')
    else:
        form = CadastrarAdministradorForm()
    return render(request, 'cadastrar_administrador.html', {'form': form})

def listar_administradores(request):
    administradores = Administrador.objects.all()
    return render(request, 'listar_administradores.html', {'administradores': administradores})

def login_administrador(request):
    if request.method == 'POST':
        nome_usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=nome_usuario, password=senha)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('painel_admin')
        else:
            messages.error(request, "Credenciais inválidas ou sem permissão.")
    return render(request, 'login_administrador.html')

@login_required
def logout_administrador(request):
    logout(request)
    return redirect('index')

def buscar_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    return render(request, 'detalhes_administrador.html', {'administrador': administrador})

def editar_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == 'POST':
        form = CadastrarAdministradorForm(request.POST, instance=administrador)
        if form.is_valid():
            form.save()
            messages.success(request, "Administrador atualizado com sucesso.")
            return redirect('listar_administradores')
    else:
        form = CadastrarAdministradorForm(instance=administrador)
    return render(request, 'editar_administrador.html', {'form': form})

def excluir_administrador(request, pk):
    administrador = get_object_or_404(Administrador, pk=pk)
    if request.method == 'POST':
        administrador.delete()
        messages.success(request, "Administrador excluído com sucesso.")
        return redirect('listar_administradores')
    return render(request, 'excluir_administrador.html', {'administrador': administrador})

# --- ORGAOS ---

@login_required
def listar_orgaos(request):
    orgaos = Orgao.objects.all()
    return render(request, 'orgaos/listar_orgaos.html', {'orgaos': orgaos})

@login_required
def adicionar_orgao(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')

        if nome:
            Orgao.objects.create(nome=nome, descricao=descricao)
            messages.success(request, "Órgão adicionado com sucesso.")
            return redirect('listar_orgaos')
        else:
            messages.error(request, "O nome do órgão é obrigatório.")

    return render(request, 'orgaos/adicionar_orgao.html')

@login_required
def editar_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    if request.method == 'POST':
        orgao.nome = request.POST.get('nome')
        orgao.descricao = request.POST.get('descricao')
        orgao.save()
        messages.success(request, "Órgão atualizado com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'orgaos/editar_orgao.html', {'orgao': orgao})

@login_required
def excluir_orgao(request, pk):
    orgao = get_object_or_404(Orgao, pk=pk)
    if request.method == 'POST':
        orgao.delete()
        messages.success(request, "Órgão excluído com sucesso.")
        return redirect('listar_orgaos')
    return render(request, 'orgaos/excluir_orgao.html', {'orgao': orgao})

@login_required
def painel_admin(request):
    return render(request, 'painel_admin.html')

@login_required
def listar_centros(request):
    centros = CentroDistribuicao.objects.all()
    return render(request, 'centros/listar_centros.html', {'centros': centros})

@login_required
def editar_centro(request, pk):
    centro = get_object_or_404(CentroDistribuicao, pk=pk)
    if request.method == 'POST':
        centro.nome = request.POST.get('nome')
        centro.estado = request.POST.get('estado')
        centro.cidade = request.POST.get('cidade')
        centro.save()
        messages.success(request, "Centro atualizado com sucesso.")
        return redirect('listar_centros')
    return render(request, 'centros/editar_centro.html', {'centro': centro})

