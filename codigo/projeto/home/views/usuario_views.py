# home/views/usuario_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

# --- NOVAS IMPORTAÇÕES ---
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.http import JsonResponse
# -------------------------

# --- IMPORTS DOS SEUS FORMULÁRIOS (MODIFICADO) ---
try:
    from ..forms import UsuarioCadastroForm
    from ..forms import UsuarioEditarPerfilForm 
except ImportError:
    from ..forms.usuario_forms import UsuarioCadastroForm
    from ..forms.usuario_forms import UsuarioEditarPerfilForm 
from ..forms.perfil_forms import UsuarioFocoForm
# ------------------------------------

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from decimal import Decimal

# --- IMPORTS DOS SEUS MODELS ---
from ..models.usuario_foco import UsuarioFoco
from ..models import Usuario
# -------------------------------

# --- IMPORT NECESSÁRIO PARA O LOGGER ---
import logging
logger = logging.getLogger(__name__)
# -------------------------------------

# --- FUNÇÕES ORIGINAIS DO USUÁRIO ---

def index(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')

# --- VIEW HOME ATUALIZADA (COM DADOS DE NÍVEL) ---
@login_required
def home(request):
    user = request.user
    now = timezone.now()

    # Define a hora de "corte" (22h)
    HORA_CORTE = time(22, 0, 0)

    # Determina o início do "dia de foco" atual
    if now.time() < HORA_CORTE:
        # Se for antes das 22h, o dia de foco começou ontem às 22h
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        # Se for 22h ou mais, o dia de foco começou hoje às 22h
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    # Determina o início do dia de foco ANTERIOR (para checar a quebra de streak)
    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)

    ultimo_resgate = user.ultimo_resgate_foco
    pode_resgatar = True

    # 1. Lógica de Reset (Quebra de Streak)
    if ultimo_resgate is not None:
        if ultimo_resgate < inicio_dia_foco_anterior:
            # O último resgate foi antes do início do dia de foco anterior
            # Ou seja, o usuário pulou um dia. Zera a contagem.
            user.dias_foco = 0
            user.save(update_fields=['dias_foco'])
    
    # 2. Lógica do Botão (Verifica se já resgatou HOJE)
    if ultimo_resgate is not None:
        if ultimo_resgate >= inicio_dia_foco_atual:
            # O último resgate foi dentro do "dia de foco" atual.
            pode_resgatar = False

    # --- MUDANÇA AQUI ---
    # Passa os dados de nível e XP para o template
    context = {
        'pode_resgatar': pode_resgatar,
        'nivel_usuario': user.nivel,
        'xp_usuario': user.xp_atual,
        'xp_necessario': user.xp_proximo_nivel,
    }
    return render(request, 'home/home.html', context)
# --- FIM DA VIEW HOME ---


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    if request.method == 'POST':
        email_ou_username = request.POST.get('email')
        password = request.POST.get('senha')
        if not email_ou_username or not password:
            messages.error(request, 'Por favor, preencha o e-mail/usuário e a senha.')
            form = AuthenticationForm()
            # (Ajustes do form para o GET)
            form.fields['username'].label = "Email ou Usuário"; form.fields['username'].widget.attrs.update({'placeholder': 'Digite seu email ou usuário', 'id': 'email', 'name': 'email'})
            form.fields['password'].label = "Senha"; form.fields['password'].widget.attrs.update({'placeholder': 'Digite sua senha', 'id': 'senha', 'name': 'senha'})
            return render(request, 'home/login.html', {'form': form})
        
        # --- ATENÇÃO ---
        # Sua view de login usa 'authenticate' com 'username=email_ou_username'
        # Mas seu USERNAME_FIELD é 'email'.
        # O 'authenticate' padrão pode falhar.
        # Você deve ter um backend de autenticação customizado ou deve 
        # tentar logar especificamente com o email.
        # Vamos tentar encontrar o usuário pelo email primeiro:
        try:
            user_pelo_email = Usuario.objects.get(email=email_ou_username)
            user = authenticate(request, username=user_pelo_email.email, password=password)
        except Usuario.DoesNotExist:
            user = None # Usuário não encontrado
            
        if user is not None:
            login(request, user)
            nome_display = getattr(user, 'nome_usuario', user.email) # Usa email como fallback
            messages.success(request, f'Bem-vindo de volta, {nome_display}!')
            return redirect('home:home')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')
            # (O resto da lógica de erro estava aqui, mas é melhor simplificar)
    
    form = AuthenticationForm()
    # Modifica os campos do form para o GET
    form.fields['username'].label = "Email ou Usuário"
    form.fields['username'].widget.attrs.update({'placeholder': 'Digite seu email ou usuário', 'id': 'email', 'name': 'email'})
    form.fields['password'].label = "Senha"
    form.fields['password'].widget.attrs.update({'placeholder': 'Digite sua senha', 'id': 'senha', 'name': 'senha'})
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
            # O 'form.save()' já deve ter setado a senha (se for um ModelForm do seu Usuario)
            # Se o 'save()' do form não loga automaticamente, fazemos o login manual
            login(request, user, backend='django.contrib.auth.backends.ModelBackend') # Especifica o backend
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

# --- FIM DAS FUNÇÕES ORIGINAIS ---

# -------------------------------------------------------------------
# --- NOVA VIEW ADICIONADA ---
# -------------------------------------------------------------------
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        # Carrega o formulário com os dados do POST e a instância do usuário atual
        form = UsuarioEditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            # 1. Salva o formulário e captura o objeto 'user' atualizado
            user = form.save() 
            messages.success(request, 'Perfil atualizado com sucesso!')
            
            # 2. ATUALIZA A SESSÃO 
            # Isso força o 'request.user' a ter os novos dados em todas as páginas
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            return redirect('home:editar_perfil') # Redireciona para a mesma página
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos.')
    else:
        # (Método GET) Cria o formulário pré-preenchido com os dados do usuário
        form = UsuarioEditarPerfilForm(instance=request.user)

    context = {
        'form': form
    }
    # O caminho do template que você criou
    return render(request, 'home/editar_perfil.html', context)


# --- [MODIFICADO] FUNÇÃO PARA GERENCIAR O PERFIL/FOCOS ---
@login_required
def gerenciar_meu_perfil_focos(request): 
    perfis_atuais = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')
    perfis_atuais_dict = {}
    for perfil in perfis_atuais:
        dados_js = perfil.dados_especificos if isinstance(perfil.dados_especificos, dict) else {}
        for key, value in dados_js.items():
            if isinstance(value, Decimal):
                dados_js[key] = str(value) # Converte Decimal para string para o JSON
        perfis_atuais_dict[perfil.foco_nome] = {
            'foco_nome': perfil.foco_nome,
            'dados_especificos': dados_js,
            'detalhes': perfil.detalhes
        }

    if request.method == 'POST':
        foco_nome_post = request.POST.get('foco_nome')
        if not foco_nome_post:
            messages.error(request, "O campo 'Qual é o Foco?' é obrigatório.")
            form = UsuarioFocoForm() # Form vazio
            context = { 'perfis_atuais': perfis_atuais, 'form': form, 'perfis_atuais_dict': perfis_atuais_dict }
            # --- 1ª CORREÇÃO AQUI ---
            # Caminho exato que você informou
            return render(request, 'home/perfil usuario/meu_perfil.html', context) 

        instance_existente = UsuarioFoco.objects.filter(user=request.user, foco_nome=foco_nome_post).first()
        form = UsuarioFocoForm(request.POST, instance=instance_existente)

        if form.is_valid():
            # --- LÓGICA DE EXTRAÇÃO MANUAL (PARA EVITAR O ERRO DECIMAL) ---
            try:
                foco_selecionado = form.cleaned_data['foco_nome']
                dados_especificos_para_salvar = {}
                
                # Pega o mapa de campos do próprio formulário (se existir)
                if hasattr(form, 'campos_especificos_map'):
                    campos_deste_foco = form.campos_especificos_map.get(foco_selecionado, [])
                    for campo in campos_deste_foco:
                        valor = form.cleaned_data.get(campo)
                        if valor is not None and valor != '': 
                            # === A CORREÇÃO CRÍTICA ===
                            # Converte Decimal para string ANTES de salvar
                            if isinstance(valor, Decimal):
                                dados_especificos_para_salvar[campo] = str(valor)
                            else:
                                dados_especificos_para_salvar[campo] = valor
                
                # Usa update_or_create para salvar manualmente
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
                
                return redirect('home:meu_perfil_focos') # <-- Aponta para o novo nome da URL
            
            except Exception as e:
                # Agora o logger.exception funcionará
                logger.exception(f"Erro ao salvar UsuarioFocoForm manually:")
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")
            # --- FIM DA LÓGICA DE EXTRAÇÃO MANUAL ---

        else: # Form inválido
            logger.warning(f"UsuarioFocoForm inválido: {form.errors.as_json()}")
            messages.error(request, "Erro ao salvar. Verifique os campos.")
            # O form já contém os erros e os dados preenchidos pelo usuário

    else: # GET request
        form = UsuarioFocoForm()

    context = {
        'perfis_atuais': perfis_atuais,
        'form': form, # Contém erros se for POST inválido
        'perfis_atuais_dict': perfis_atuais_dict
    }
    # --- 2ª CORREÇÃO AQUI ---
    # Caminho exato que você informou
    return render(request, 'home/perfil usuario/meu_perfil.html', context)


# --- VIEW PARA RESGATAR O FOCO (MODIFICADA) ---
@login_required
def resgatar_foco(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    user = request.user
    now = timezone.now()
    
    # (Lógica de tempo duplicada para garantir segurança na API)
    HORA_CORTE = time(22, 0, 0)
    if now.time() < HORA_CORTE:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    ultimo_resgate = user.ultimo_resgate_foco

    # Verifica se já resgatou neste "dia de foco"
    if ultimo_resgate is not None and ultimo_resgate >= inicio_dia_foco_atual:
        return JsonResponse({'success': False, 'message': 'Você já resgatou seu foco hoje.'}, status=400)

    # Verifica se a streak deve ser resetada ANTES de adicionar
    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)
    if ultimo_resgate is not None and ultimo_resgate < inicio_dia_foco_anterior:
        user.dias_foco = 0 # Zera a streak

    
    # --- MUDANÇAS AQUI ---
    
    # 1. Aplica a recompensa de XP usando o método do modelo
    #     Isso já vai cuidar do level up automaticamente
    user.adicionar_xp(20) # Em vez de: user.xp_atual += 20
    
    # 2. Atualiza os outros campos
    user.dias_foco += 1
    user.ultimo_resgate_foco = now
    
    # 3. Salva todos os campos que podem ter sido alterados
    user.save(update_fields=[
        'dias_foco', 
        'xp_atual', 
        'ultimo_resgate_foco',
        'nivel',              # NOVO (afetado pelo adicionar_xp)
        'xp_proximo_nivel'    # NOVO (afetado pelo adicionar_xp)
    ])

    # 4. Retorna os novos dados (incluindo nível) para o front-end
    return JsonResponse({
        'success': True,
        'dias_foco': user.dias_foco,
        'xp_atual': user.xp_atual,
        'nivel': user.nivel,                # NOVO
        'xp_proximo_nivel': user.xp_proximo_nivel  # NOVO
    })
# --- FIM DA NOVA VIEW ---