# home/views/usuario_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

from django.utils import timezone
from datetime import datetime, timedelta, time
from django.http import JsonResponse

try:
    from ..forms import UsuarioCadastroForm
    from ..forms import UsuarioEditarPerfilForm
except ImportError:
    from ..forms.usuario_forms import UsuarioCadastroForm
    from ..forms.usuario_forms import UsuarioEditarPerfilForm
from ..forms.perfil_forms import UsuarioFocoForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from decimal import Decimal

from ..models.usuario_foco import UsuarioFoco
from ..models import Usuario

import logging
logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')


@login_required
def home(request):
    user = request.user
    now = timezone.now()

    HORA_CORTE = time(22, 0, 0)

    if now.time() < HORA_CORTE:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)

    ultimo_resgate = user.ultimo_resgate_foco
    pode_resgatar = True

    if ultimo_resgate is not None:
        if ultimo_resgate < inicio_dia_foco_anterior:
            user.dias_foco = 0
            user.save(update_fields=['dias_foco'])

    if ultimo_resgate is not None:
        if ultimo_resgate >= inicio_dia_foco_atual:
            pode_resgatar = False

    context = {
        'pode_resgatar': pode_resgatar,
        'nivel_usuario': user.nivel,
        'xp_usuario': user.xp_atual,
        'xp_necessario': user.xp_proximo_nivel,
    }
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
                nome_display = getattr(user, 'nome_usuario', user.email)
                messages.success(request, f'Bem-vindo de volta, {nome_display}!')
                return redirect('home:home')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            first_error = next(iter(form.errors.values()), ["Nome de usuário ou senha inválidos."])[0]
            messages.error(request, first_error)
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home:index')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend_path)
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a)!')
            return redirect('home:home')
        else:
            first_error = next(iter(form.errors.values()))[0] if form.errors else "Erro no cadastro."
            messages.error(request, f"Erro no cadastro: {first_error}")
    else:
        form = UsuarioCadastroForm()
    return render(request, 'home/cadastro.html', {'form': form})


def termos(request):
    return render(request, 'home/termosdeuso.html')


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UsuarioEditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('home:editar_perfil')
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos.')
    else:
        form = UsuarioEditarPerfilForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'home/editar_perfil.html', context)


@login_required
def gerenciar_meu_perfil(request):
    perfis_atuais = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')
    perfis_atuais_dict = {}
    for perfil in perfis_atuais:
        dados_js = perfil.dados_especificos if isinstance(perfil.dados_especificos, dict) else {}
        for key, value in dados_js.items():
            if isinstance(value, Decimal):
                dados_js[key] = str(value)
        perfis_atuais_dict[perfil.foco_nome] = {
            'foco_nome': perfil.foco_nome,
            'dados_especificos': dados_js,
            'detalhes': perfil.detalhes
        }

    if request.method == 'POST':
        foco_nome_post = request.POST.get('foco_nome')
        if not foco_nome_post:
            messages.error(request, "O campo 'Qual é o Foco?' é obrigatório.")
            form = UsuarioFocoForm()
            context = { 'perfis_atuais': perfis_atuais, 'form': form, 'perfis_atuais_dict': perfis_atuais_dict }
            return render(request, 'home/perfil usuario/meu_perfil.html', context)

        instance_existente = UsuarioFoco.objects.filter(user=request.user, foco_nome=foco_nome_post).first()
        form = UsuarioFocoForm(request.POST, instance=instance_existente)

        if form.is_valid():
            try:
                foco_selecionado = form.cleaned_data['foco_nome']
                dados_especificos_para_salvar = {}

                if hasattr(form, 'campos_especificos_map'):
                    campos_deste_foco = form.campos_especificos_map.get(foco_selecionado, [])
                    for campo in campos_deste_foco:
                        valor = form.cleaned_data.get(campo)
                        if valor is not None and valor != '':
                            if isinstance(valor, Decimal):
                                dados_especificos_para_salvar[campo] = str(valor)
                            else:
                                dados_especificos_para_salvar[campo] = valor

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

            except Exception as e:
                logger.exception(f"Erro ao salvar UsuarioFocoForm manually:")
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")

        else:
            logger.warning(f"UsuarioFocoForm inválido: {form.errors.as_json()}")
            messages.error(request, "Erro ao salvar. Verifique os campos.")

    else:
        form = UsuarioFocoForm()

    context = {
        'perfis_atuais': perfis_atuais,
        'form': form,
        'perfis_atuais_dict': perfis_atuais_dict
    }
    return render(request, 'home/perfil usuario/meu_perfil.html', context)


@login_required
def resgatar_foco(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    user = request.user
    now = timezone.now()

    HORA_CORTE = time(22, 0, 0)
    if now.time() < HORA_CORTE:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    ultimo_resgate = user.ultimo_resgate_foco

    if ultimo_resgate is not None and ultimo_resgate >= inicio_dia_foco_atual:
        return JsonResponse({'success': False, 'message': 'Você já resgatou seu foco hoje.'}, status=400)

    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)
    if ultimo_resgate is not None and ultimo_resgate < inicio_dia_foco_anterior:
        user.dias_foco = 0

    user.adicionar_xp(20)

    user.dias_foco += 1
    user.ultimo_resgate_foco = now

    user.save(update_fields=[
        'dias_foco',
        'xp_atual',
        'ultimo_resgate_foco',
        'nivel',
        'xp_proximo_nivel'
    ])

    return JsonResponse({
        'success': True,
        'dias_foco': user.dias_foco,
        'xp_atual': user.xp_atual,
        'nivel': user.nivel,
        'xp_proximo_nivel': user.xp_proximo_nivel
    })