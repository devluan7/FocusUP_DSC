# home/views/tarefa_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from datetime import time, datetime # <-- datetime ADICIONADO
from django.utils import timezone
from ..models import Tarefa, UsuarioFoco, Conquista, UsuarioConquista
from ..forms import TarefaForm
from ..ai_engine import FocusAIEngine, TarefaSugerida
import json
import logging
import locale # <-- ADICIONADO PARA O DIA DA SEMANA

logger = logging.getLogger(__name__)

# --- Função de conquistas ---
def verificar_e_conceder_conquistas_de_tarefas(usuario):
    # (Código da função igual ao anterior)
    try:
        tarefas_concluidas_count = Tarefa.objects.filter(usuario=usuario, concluida=True).count()
        conquistas_por_tarefas = { "Iniciante Esforçado": 1, "Mestre das 5 Tarefas": 5, "Produtividade em Pessoa": 10, "Lenda das 25 Tarefas": 25,}
        for nome_conquista, criterio_count in conquistas_por_tarefas.items():
            if tarefas_concluidas_count >= criterio_count:
                possui_conquista = UsuarioConquista.objects.filter(usuario=usuario, conquista__nome=nome_conquista).exists()
                if not possui_conquista:
                    conquista, created = Conquista.objects.get_or_create( nome=nome_conquista, defaults={'criterio': f'Concluir {criterio_count} tarefas.', 'xp_points': criterio_count * 10} )
                    UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)
                    logger.info(f"Conquista '{nome_conquista}' concedida para usuário ID {usuario.pk}!")
    except Exception as e:
        logger.error(f"Erro ao verificar conquistas para usuário ID {getattr(usuario, 'pk', 'N/A')}: {e}", exc_info=True)


# --- View lista_Tarefas ---
@login_required
def lista_Tarefas(request):
    # (Código da view igual ao anterior, filtrando concluida=False)
    tarefas_do_usuario = []
    perfis_usuario = []
    erro_carregamento = False
    try:
        tarefas_do_usuario = Tarefa.objects.filter(usuario=request.user, concluida=False).order_by('-data_criacao')
        perfis_usuario = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')
    except Exception as e:
        logger.exception(f"Erro ao carregar dados para lista_Tarefas (usuário ID: {getattr(request.user, 'pk', 'N/A')}):")
        messages.error(request, "Ocorreu um erro ao carregar seus dados. Tente novamente.")
        erro_carregamento = True
    contexto = { 'tarefas': tarefas_do_usuario, 'perfis_usuario': perfis_usuario, 'erro_carregamento': erro_carregamento }
    return render(request, 'home/tarefas/lista_Tarefas.html', contexto) # Verifique caminho!


# --- View adicionar_Tarefas ---
@login_required
def adicionar_Tarefas(request):
    try:
        perfis_usuario = UsuarioFoco.objects.filter(user=request.user)
        form = TarefaForm(request.POST or None)

        if request.method == 'POST':
            action = None; data = {}; is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json'
            if is_ajax and request.headers.get('Content-Type') == 'application/json':
                try: data = json.loads(request.body); action = data.get('action')
                except json.JSONDecodeError: logger.warning("POST JSON inválido."); return JsonResponse({'error': 'JSON inválido.'}, status=400)
            elif not is_ajax: action = 'salvar_manual'
            else: logger.warning(f"POST AJAX Content-Type inesperado"); return JsonResponse({'error': 'Tipo requisição inválida.'}, status=400)

            # --- CASO 1: AJAX para Gerar Sugestão IA (ATUALIZADO) ---
            if action == 'gerar_sugestao':
                foco_nome = data.get('foco_nome'); logger.info(f"AJAX gerar IA. Foco: {foco_nome}")
                try:
                    if not foco_nome: return JsonResponse({'error': 'Foco não fornecido.'}, status=400)
                    perfil_foco = get_object_or_404(UsuarioFoco, user=request.user, foco_nome=foco_nome)
                    
                    # --- MUDANÇA AQUI: Adiciona dia da semana ---
                    try:
                        # Tenta configurar o locale para Português do Brasil
                        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
                    except locale.Error:
                        logger.warning("Locale 'pt_BR.UTF-8' não encontrado, tentando 'Portuguese_Brazil.1252' (Windows).")
                        try:
                            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
                        except locale.Error:
                            logger.warning("Locale do Windows não encontrado, usando padrão 'C'.")
                            locale.setlocale(locale.LC_TIME, 'C') # Fallback
                    
                    # Pega o dia da semana atual em português (ex: "terça-feira")
                    dia_da_semana = datetime.now().strftime('%A').lower()
                    # --- FIM MUDANÇA ---

                    perfil_dict = {
                        "foco_nome": perfil_foco.foco_nome,
                        "detalhes": perfil_foco.detalhes,
                        "dados_especificos": perfil_foco.dados_especificos or {},
                        "dia_da_semana": dia_da_semana # <-- Passa o dia da semana para a IA
                    }

                    engine = FocusAIEngine(); sugestao = engine.gerar_sugestao_tarefa_diaria(perfil_dict)
                    if sugestao: return JsonResponse({'titulo': sugestao.titulo, 'descricao': sugestao.descricao_motivacional,'dificuldade': sugestao.dificuldade, 'xp': sugestao.xp_calculado})
                    else: return JsonResponse({'error': 'IA não gerou sugestão.'}, status=500)
                except UsuarioFoco.DoesNotExist: return JsonResponse({'error': f'Perfil "{foco_nome}" não encontrado.'}, status=404)
                except Exception as e: logger.exception("Erro AJAX gerar IA:"); return JsonResponse({'error': 'Erro interno ao gerar.'}, status=500)

            # --- CASO 2: AJAX para Salvar Sugestão da IA ---
            elif action == 'salvar_sugestao':
                 # (Código igual ao anterior)
                 titulo = data.get('titulo'); descricao = data.get('descricao')
                 xp_recebido = data.get('xp', 10)
                 logger.info(f"AJAX salvar sugestão IA: '{titulo}' (XP: {xp_recebido})")
                 if not titulo or not descricao: return JsonResponse({'error': 'Dados faltando.'}, status=400)
                 try:
                     nova_tarefa = Tarefa.objects.create( usuario=request.user, titulo=titulo, descricao=descricao, frequencia='diaria', hora_lembrete=time(9, 0), xp=int(xp_recebido), concluida=False )
                     logger.info(f"Tarefa sugerida '{titulo}' salva com PK {nova_tarefa.pk}.")
                     return JsonResponse({ 'success': True, 'tarefa_id': nova_tarefa.pk, 'titulo': nova_tarefa.titulo, 'frequencia_display': nova_tarefa.get_frequencia_display(), 'hora_lembrete': nova_tarefa.hora_lembrete.strftime('%H:%M') if nova_tarefa.hora_lembrete else '', 'url_concluir': reverse('home:concluir_tarefa', args=[nova_tarefa.pk]), 'descricao_completa': nova_tarefa.descricao, 'xp_adicionado': nova_tarefa.xp })
                 except Exception as e: logger.exception("Erro CRÍTICO AJAX salvar sugestão:"); return JsonResponse({'error': 'Erro ao salvar tarefa.'}, status=500)

            # --- CASO 3: Submissão Normal do Formulário HTML ---
            elif action == 'salvar_manual':
                # (Código igual ao anterior)
                if form.is_valid():
                    nova_tarefa = form.save(commit=False); nova_tarefa.usuario = request.user;
                    nova_tarefa.save() 
                    messages.success(request, 'Tarefa adicionada!'); return redirect('home:lista_Tarefas')
                else:
                    context = { 'form': form, 'perfis_usuario': perfis_usuario }; messages.error(request, 'Corrija os erros.'); return render(request, 'home/tarefas/adicionar_Tarefas.html', context)
            else:
                # (Código igual ao anterior)
                if is_ajax: return JsonResponse({'error': 'Ação inválida.'}, status=400)
                else: messages.error(request, 'Ação inválida.'); context = { 'form': form, 'perfis_usuario': perfis_usuario }; return render(request, 'home/tarefas/adicionar_Tarefas.html', context)
        
        # --- Lógica GET ---
        else: # request.method == 'GET'
            context = { 'form': form, 'perfis_usuario': perfis_usuario }
            return render(request, 'home/tarefas/adicionar_Tarefas.html', context)
    except Exception as e:
        logger.exception(f"Erro GERAL adicionar_Tarefas:"); messages.error(request, "Erro inesperado."); return redirect('home:lista_Tarefas')


# --- View concluir_tarefa (Atualizada para XP) ---
@login_required
def concluir_tarefa(request, tarefa_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"--- Iniciando concluir_tarefa para PK {tarefa_id} (AJAX: {is_ajax}) ---")

    if request.method != 'POST':
        if is_ajax: return JsonResponse({'error': 'Método não permitido.'}, status=405)
        else: messages.warning(request, "Ação inválida."); return redirect('home:lista_Tarefas')

    try:
        tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
        logger.info(f"Tarefa encontrada: '{tarefa.titulo}', Concluída antes: {tarefa.concluida}")
        era_concluida_antes = tarefa.concluida
        novo_estado = not tarefa.concluida
        tarefa.concluida = novo_estado
        
        xp_ganho = 0
        usuario_obj = request.user
        usuario_xp_total = usuario_obj.xp_atual or 0

        if not era_concluida_antes and tarefa.concluida: # MARCANDO como concluída
            try:
                xp_ganho = tarefa.xp
                usuario_xp_total = usuario_xp_total + xp_ganho
                usuario_obj.xp_atual = usuario_xp_total
                usuario_obj.save(update_fields=['xp_atual']) # Salva SÓ o XP
                logger.info(f"Usuário ID {usuario_obj.pk} ganhou {xp_ganho} XP. Total: {usuario_xp_total}")
            except Exception as e_xp:
                logger.error(f"Erro ao adicionar XP: {e_xp}", exc_info=True)
        
        elif era_concluida_antes and not tarefa.concluida: # DESMARCANDO
            try:
                xp_perdido = tarefa.xp
                usuario_xp_total = max(0, usuario_xp_total - xp_perdido) # Não fica negativo
                xp_ganho = -xp_perdido
                usuario_obj.xp_atual = usuario_xp_total
                usuario_obj.save(update_fields=['xp_atual'])
                logger.info(f"Usuário ID {usuario_obj.pk} perdeu {xp_perdido} XP. Total: {usuario_xp_total}")
            except Exception as e_xp:
                 logger.error(f"Erro ao remover XP: {e_xp}", exc_info=True)

        logger.info(f"Tentando salvar tarefa PK {tarefa.pk} com concluida = {novo_estado}...")
        tarefa.save() # Salva a tarefa (o save custom do modelo lida com data_conclusao)
        logger.info(f"Tarefa PK {tarefa.pk} SALVA!")

        if not era_concluida_antes and tarefa.concluida:
            logger.info("Verificando conquistas...")
            try: verificar_e_conceder_conquistas_de_tarefas(request.user)
            except Exception as e_conq: logger.error(f"Erro conquistas: {e_conq}", exc_info=True)

        if is_ajax:
            logger.info("Retornando JSON de sucesso para AJAX.")
            return JsonResponse({ 'success': True, 'concluida': tarefa.concluida, 'xp_ganho': xp_ganho, 'xp_total_usuario': usuario_xp_total })
        else:
            status_msg = "concluída" if tarefa.concluida else "pendente"
            if xp_ganho > 0: messages.success(request, f'Tarefa "{tarefa.titulo}" {status_msg}! (+{xp_ganho} XP)')
            else: messages.success(request, f'Tarefa "{tarefa.titulo}" {status_msg}.')
            return redirect('home:lista_Tarefas')

    except Tarefa.DoesNotExist:
         logger.warning(f"Tarefa PK {tarefa_id} não encontrada!")
         if is_ajax: return JsonResponse({'error': 'Tarefa não encontrada.'}, status=404)
         else: messages.error(request, "Tarefa não encontrada."); return redirect('home:lista_Tarefas')
    except Exception as e:
        logger.exception(f"Erro GERAL concluir_tarefa (pk={tarefa_id}):")
        if is_ajax: return JsonResponse({'error': 'Erro interno.'}, status=500)
        else: messages.error(request, "Erro ao alterar status."); return redirect('home:lista_Tarefas')