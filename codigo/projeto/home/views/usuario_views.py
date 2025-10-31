# home/views/usuario_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings # Importa settings

try:
    from ..forms import UsuarioCadastroForm
except ImportError:
    from ..forms.usuario_forms import UsuarioCadastroForm

from ..forms.perfil_forms import UsuarioFocoForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from decimal import Decimal
from ..models.usuario_foco import UsuarioFoco


def index(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')

@login_required
def home(request):
    context = {}
    return render(request, 'home/home.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Tenta pegar 'nome_usuario', se não existir, pega 'email'
                nome_display = getattr(user, 'nome_usuario', user.email)
                messages.success(request, f'Bem-vindo de volta, {nome_display}!')
                return redirect('home:home')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home:index')

# Função cadastro (Processa o formulário de cadastro)
# A linha duplicada "def cadastro(request):" foi REMOVIDA daqui
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Especifica o backend ao logar
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend_path) # Correção mantida
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a)!')
            return redirect('home:home')
        else:
            error_msg = "Erro no cadastro. Verifique os dados informados."
            # Opcional: Mostrar erros específicos do formulário
            # error_detail = form.errors.as_text()
            # messages.error(request, f"{error_msg} Detalhes: {error_detail}")
            messages.error(request, error_msg)
    else:
        form = UsuarioCadastroForm()
    return render(request, 'home/cadastro.html', {'form': form})

def termos(request):
    return render(request, 'home/termosdeuso.html')

@login_required
def gerenciar_meu_perfil(request):
    """
    Página onde o usuário configura seus focos para a IA.
    Salva dados específicos no JSONField, convertendo Decimal para string.
    """
    perfis_atuais = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')

    perfis_atuais_dict = {
        perfil.foco_nome: {
            'dados_especificos': perfil.dados_especificos,
            'detalhes': perfil.detalhes
        }
        for perfil in perfis_atuais
    }

    if request.method == 'POST':
        foco_nome_post = request.POST.get('foco_nome')
        instance_existente = UsuarioFoco.objects.filter(user=request.user, foco_nome=foco_nome_post).first()
        form = UsuarioFocoForm(request.POST, instance=instance_existente)

        if form.is_valid():
            foco_selecionado = form.cleaned_data['foco_nome']
            dados_especificos_para_salvar = {}

            if foco_selecionado == 'academia':
                campos_academia = ['altura', 'peso', 'nivel_treino', 'local_treino', 'freq_treino', 'objetivo_academia']
                for campo in campos_academia:
                    valor = form.cleaned_data.get(campo)
                    if valor is not None and valor != '':
                        if isinstance(valor, Decimal):
                            dados_especificos_para_salvar[campo] = str(valor) # Converte Decimal
                        else:
                            dados_especificos_para_salvar[campo] = valor
            # Adicione 'elif' para outros focos específicos aqui

            perfil, criado = UsuarioFoco.objects.update_or_create(
                user=request.user,
                foco_nome=foco_selecionado,
                defaults={
                    'dados_especificos': dados_especificos_para_salvar,
                    'detalhes': form.cleaned_data['detalhes']
                }
            )
            if criado:
                messages.success(request, f"Novo foco '{foco_selecionado}' salvo com sucesso!")
            else:
                messages.success(request, f"Foco '{foco_selecionado}' atualizado com sucesso!")
            return redirect('home:meu_perfil')
        else:
            messages.error(request, "Erro ao salvar. Por favor, verifique os campos e tente novamente.")

    else: # GET request
        form = UsuarioFocoForm()

    context = {
        'perfis_atuais': perfis_atuais,
        'form': form,
        'perfis_atuais_dict': perfis_atuais_dict
    }

    return render(request, 'home/perfil usuario/meu_perfil.html', context)