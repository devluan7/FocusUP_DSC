# home/views/tarefa_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from datetime import time, datetime 
from django.utils import timezone
from ..models import Tarefa, UsuarioFoco, Conquista, UsuarioConquista, Usuario
from ..forms import TarefaForm
from ..ai_engine import FocusAIEngine, TarefaSugerida
from ..tasks.motor_tasks import processar_slots_diarios
import json
import logging
import locale 

logger = logging.getLogger(__name__)


def verificar_e_conceder_conquistas_de_tarefas(usuario):
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


@login_required
def lista_Tarefas(request):
    tarefas_do_usuario = []
    perfis_usuario = []
    erro_carregamento = False
    try:
        processar_slots_diarios(request.user)
        slots_usados_hoje = request.user.slots_tarefas_pessoais_usados
    except Exception as e:
        logger.exception(f"Erro ao processar slots para o usuário {request.user.email}")
        slots_usados_hoje = 0 
    try:
        tarefas_do_usuario = Tarefa.objects.filter(
            usuario=request.user, 
            concluida=False,
            descartada=False, 
            tipo_tarefa__in=['PESSOAL', 'DIARIA'] 
        ).order_by('-data_criacao')
        perfis_usuario = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')
    except Exception as e:
        logger.exception(f"Erro ao carregar dados para lista_Tarefas (usuário ID: {getattr(request.user, 'pk', 'N/A')}):")
        messages.error(request, "Ocorreu um erro ao carregar seus dados. Tente novamente.")
        erro_carregamento = True
    contexto = { 
        'tarefas': tarefas_do_usuario, 
        'perfis_usuario': perfis_usuario, 
        'erro_carregamento': erro_carregamento,
        'slots_usados': slots_usados_hoje,
        'slots_limite': Usuario.LIMITE_SLOTS_PESSOAIS 
    }
    return render(request, 'home/tarefas/lista_Tarefas.html', contexto)


@login_required
def adicionar_Tarefas(request):
    try:
        perfis_usuario = UsuarioFoco.objects.filter(user=request.user)
        form = TarefaForm(request.POST or None)
        try:
            slots_usados_hoje = request.user.resetar_slots_tarefas_pessoais()
        except Exception as e:
            logger.exception(f"Erro ao resetar slots para o usuário {request.user.email} em adicionar_Tarefas")
            slots_usados_hoje = Usuario.LIMITE_SLOTS_PESSOAIS 
        if request.method == 'POST':
            action = None; data = {}; is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json'
            if not is_ajax: 
                action = 'salvar_manual'
            else:
                try: data = json.loads(request.body); action = data.get('action')
                except json.JSONDecodeError: logger.warning("POST JSON inválido."); return JsonResponse({'error': 'JSON inválido.'}, status=400)
            if action == 'salvar_sugestao':
                if slots_usados_hoje >= Usuario.LIMITE_SLOTS_PESSOAIS:
                    return JsonResponse({'error': 'Você já atingiu seu limite de 3 tarefas pessoais por hoje.'}, status=403) 
                titulo = data.get('titulo'); descricao = data.get('descricao')
                xp_recebido = data.get('xp', 10)
                if not titulo or not descricao: return JsonResponse({'error': 'Dados faltando.'}, status=400)
                try:
                    nova_tarefa = Tarefa.objects.create( 
                        usuario=request.user, titulo=titulo, descricao=descricao, 
                        frequencia='DIARIA', hora_lembrete=time(9, 0), 
                        xp=int(xp_recebido), xp_original=int(xp_recebido), 
                        tipo_tarefa='PESSOAL', concluida=False 
                    )
                    request.user.slots_tarefas_pessoais_usados += 1
                    request.user.save(update_fields=['slots_tarefas_pessoais_usados'])
                    logger.info(f"Tarefa sugerida '{titulo}' salva com PK {nova_tarefa.pk}.")
                    return JsonResponse({ 'success': True, 'tarefa_id': nova_tarefa.pk, 'titulo': nova_tarefa.titulo, 'frequencia_display': nova_tarefa.get_frequencia_display(), 'hora_lembrete': nova_tarefa.hora_lembrete.strftime('%H:%M') if nova_tarefa.hora_lembrete else '', 'url_concluir': reverse('home:concluir_tarefa', args=[nova_tarefa.pk]), 'descricao_completa': nova_tarefa.descricao, 'xp_adicionado': nova_tarefa.xp, 'slots_usados': request.user.slots_tarefas_pessoais_usados })
                except Exception as e: logger.exception("Erro CRÍTICO AJAX salvar sugestão:"); return JsonResponse({'error': 'Erro ao salvar tarefa.'}, status=500)
            elif action == 'salvar_manual':
                if form.is_valid():
                    nova_tarefa = form.save(commit=False)
                    nova_tarefa.usuario = request.user
                    nova_tarefa.tipo_tarefa = 'TEMPLATE_PESSOAL' 
                    nova_tarefa.xp = 10 
                    nova_tarefa.xp_original = 10
                    nova_tarefa.save() 
                    messages.success(request, f'Tarefa "{nova_tarefa.titulo}" criada na sua lista de pessoais!'); 
                    return redirect('home:adicionar_Tarefas')
                else:
                    tarefas_pessoais_list = Tarefa.objects.filter(usuario=request.user, tipo_tarefa='TEMPLATE_PESSOAL').order_by('titulo')
                    context = { 'form': form, 'perfis_usuario': perfis_usuario, 'slots_usados': slots_usados_hoje, 'slots_limite': Usuario.LIMITE_SLOTS_PESSOAIS, 'tarefas_pessoais_list': tarefas_pessoais_list }; 
                    messages.error(request, 'Corrija os erros.'); 
                    return render(request, 'home/tarefas/adicionar_Tarefas.html', context)
            elif action == 'gerar_sugestao':
                foco_nome = data.get('foco_nome'); 
                if not foco_nome: return JsonResponse({'error': 'Foco não fornecido.'}, status=400)
                perfil_foco = get_object_or_404(UsuarioFoco, user=request.user, foco_nome=foco_nome)
                engine = FocusAIEngine(); sugestao = engine.gerar_sugestao_tarefa_diaria({"foco_nome": foco_nome, "dia_da_semana": "hoje"}) 
                if sugestao: return JsonResponse({'titulo': sugestao.titulo, 'descricao': sugestao.descricao_motivacional,'dificuldade': sugestao.dificuldade, 'xp': sugestao.xp_calculado})
                else: return JsonResponse({'error': 'IA não gerou sugestão.'}, status=500)
            else:
                if is_ajax: return JsonResponse({'error': 'Ação inválida.'}, status=400)
                else: messages.error(request, 'Ação inválida.'); return redirect('home:adicionar_Tarefas')
        else: 
            tarefas_pessoais_list = Tarefa.objects.filter(
                usuario=request.user, 
                tipo_tarefa='TEMPLATE_PESSOAL' 
            ).order_by('titulo')
            context = { 
                'form': form, 
                'perfis_usuario': perfis_usuario, 
                'slots_usados': slots_usados_hoje, 
                'slots_limite': Usuario.LIMITE_SLOTS_PESSOAIS,
                'tarefas_pessoais_list': tarefas_pessoais_list 
            }
            return render(request, 'home/tarefas/adicionar_Tarefas.html', context)
    except Exception as e:
        logger.exception(f"Erro GERAL adicionar_Tarefas:") 
        messages.error(request, "Erro inesperado ao carregar a página."); 
        return redirect('home:lista_Tarefas')


@login_required
def concluir_tarefa(request, tarefa_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"--- Iniciando concluir_tarefa para PK {tarefa_id} (AJAX: {is_ajax}) ---")

    if request.method != 'POST':
        if is_ajax: return JsonResponse({'error': 'Método não permitido.'}, status=405)
        else: messages.warning(request, "Ação inválida."); return redirect('home:lista_Tarefas')

    try:
        tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
        usuario_obj = request.user 
        
        if tarefa.concluida:
            logger.info(f"Desmarcando tarefa PK {tarefa.pk}")
            tarefa.concluida = False
            xp_ganho = 0
            usuario_xp_total = usuario_obj.xp_atual or 0
            
            try:
                if not tarefa.falhou:
                    xp_perdido = tarefa.xp_original or tarefa.xp 
                    usuario_xp_total = max(0, usuario_xp_total - xp_perdido) 
                    xp_ganho = -xp_perdido
                    usuario_obj.xp_atual = usuario_xp_total
                    usuario_obj.tarefas_concluidas_prazo_count = max(0, usuario_obj.tarefas_concluidas_prazo_count - 1)
                    logger.info(f"Usuário ID {usuario_obj.pk} perdeu {xp_perdido} XP (PK {tarefa.pk}). Total: {usuario_xp_total}")
                else:
                    usuario_obj.tarefas_concluidas_atrasadas_count = max(0, usuario_obj.tarefas_concluidas_atrasadas_count - 1)
                    logger.info(f"Usuário ID {usuario_obj.pk} desmarcou tarefa ATRASADA (PK {tarefa.pk}).")
                
                usuario_obj.save(update_fields=['xp_atual', 'tarefas_concluidas_atrasadas_count', 'tarefas_concluidas_prazo_count'])
            
            except Exception as e_xp:
                logger.error(f"Erro ao remover XP/Contagem: {e_xp}", exc_info=True)

        else:
            logger.info(f"Marcando tarefa PK {tarefa.pk} como concluída.")
            
            if tarefa.descartada or tarefa.falhou:
                logger.warning(f"Usuário {request.user.email} tentou concluir (pela URL normal) uma tarefa que falhou ou foi descartada (PK {tarefa.pk}).")
                return JsonResponse({'error': 'Esta tarefa não pode ser concluída por esta ação.'}, status=403)

            tarefa.concluida = True
            xp_ganho = 0
            usuario_xp_total = usuario_obj.xp_atual or 0
            
            try:
                xp_ganho = tarefa.xp_original or tarefa.xp 
                usuario_obj.adicionar_xp(xp_ganho)
                
                usuario_obj.tarefas_concluidas_prazo_count += 1
                usuario_obj.save(update_fields=['tarefas_concluidas_prazo_count'])
                
                logger.info(f"Usuário ID {usuario_obj.pk} ganhou {xp_ganho} XP (PK {tarefa.pk}). Contador PRAZO: {usuario_obj.tarefas_concluidas_prazo_count}")
                
                usuario_xp_total = usuario_obj.xp_atual 
                
            except Exception as e_xp:
                logger.error(f"Erro ao adicionar XP/Contagem: {e_xp}", exc_info=True)
            
            logger.info("Verificando conquistas...")
            try: verificar_e_conceder_conquistas_de_tarefas(request.user)
            except Exception as e_conq: logger.error(f"Erro conquistas: {e_conq}", exc_info=True)

        tarefa.save() 
        logger.info(f"Tarefa PK {tarefa.pk} SALVA! (Concluida={tarefa.concluida})")

        if is_ajax:
            return JsonResponse({ 
                'success': True, 'concluida': tarefa.concluida, 'xp_ganho': xp_ganho, 
                'xp_total_usuario': usuario_xp_total, 'nivel_usuario': usuario_obj.nivel, 
                'xp_proximo_nivel': usuario_obj.xp_proximo_nivel 
            })
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


@login_required
def salvar_recorrencia(request):
    if not request.method == 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido.'}, status=405)
    try:
        data = json.loads(request.body)
        tarefa_id = data.get('tarefa_id')
        dia = data.get('dia') 
        status = data.get('status')
        if not all([tarefa_id, dia, status is not None]):
             return JsonResponse({'success': False, 'error': 'Dados incompletos.'}, status=400)
        DIAS_MAP = {
            'dom': 'recorrente_dom', 'seg': 'recorrente_seg', 'ter': 'recorrente_ter',
            'qua': 'recorrente_qua', 'qui': 'recorrente_qui', 'sex': 'recorrente_sex',
            'sab': 'recorrente_sab',
        }
        campo_para_atualizar = DIAS_MAP.get(dia)
        if not campo_para_atualizar:
            return JsonResponse({'success': False, 'error': 'Dia inválido.'}, status=400)
        tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user, tipo_tarefa='TEMPLATE_PESSOAL')
        setattr(tarefa, campo_para_atualizar, status)
        tarefa.save(update_fields=[campo_para_atualizar])
        logger.info(f"Recorrência da tarefa {tarefa.pk} atualizada: {campo_para_atualizar} = {status}")
        return JsonResponse({'success': True, 'novo_texto': tarefa.get_dias_recorrencia_display() or "Definir recorrência"})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON mal formatado.'}, status=400)
    except Tarefa.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tarefa não encontrada.'}, status=404)
    except Exception as e:
        logger.exception("Erro ao salvar recorrência:")
        return JsonResponse({'success': False, 'error': 'Erro interno no servidor.'}, status=500)


@login_required
def descartar_tarefa(request, tarefa_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"--- Iniciando DESCARTAR_tarefa para PK {tarefa_id} (AJAX: {is_ajax}) ---")
    if request.method != 'POST':
        if is_ajax: return JsonResponse({'error': 'Método não permitido.'}, status=405)
        else: messages.warning(request, "Ação inválida."); return redirect('home:lista_Tarefas')
    try:
        tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
        usuario_obj = request.user
        if not tarefa.falhou or tarefa.concluida or tarefa.descartada:
             logger.warning(f"Usuário {request.user.email} tentou descartar tarefa (PK {tarefa.pk}) que não está 'falhada'.")
             if is_ajax: return JsonResponse({'error': 'Esta tarefa não pode ser descartada.'}, status=403)
             else: messages.error(request, "Esta tarefa não pode ser descartada."); return redirect('home:lista_Tarefas')
        tarefa.descartada = True
        tarefa.save(update_fields=['descartada', 'data_acao_final']) 
        usuario_obj.tarefas_descartadas_count += 1
        usuario_obj.save(update_fields=['tarefas_descartadas_count'])
        logger.info(f"Tarefa PK {tarefa.pk} marcada como DESCARTADA. Contador: {usuario_obj.tarefas_descartadas_count}")
        if is_ajax:
            return JsonResponse({'success': True, 'descartada': True})
        else:
            messages.info(request, f'Tarefa "{tarefa.titulo}" foi descartada.')
            return redirect('home:lista_Tarefas')
    except Tarefa.DoesNotExist:
        logger.warning(f"Tarefa PK {tarefa_id} não encontrada (para descarte)!")
        if is_ajax: return JsonResponse({'error': 'Tarefa não encontrada.'}, status=404)
        else: messages.error(request, "Tarefa não encontrada."); return redirect('home:lista_Tarefas')
    except Exception as e:
        logger.exception(f"Erro GERAL descartar_tarefa (pk={tarefa_id}):")
        if is_ajax: return JsonResponse({'error': 'Erro interno.'}, status=500)
        else: messages.error(request, "Erro ao descartar tarefa."); return redirect('home:lista_Tarefas')


@login_required
def concluir_atrasado(request, tarefa_id):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"--- Iniciando CONCLUIR_ATRASADO para PK {tarefa_id} (AJAX: {is_ajax}) ---")
    if request.method != 'POST':
        if is_ajax: return JsonResponse({'error': 'Método não permitido.'}, status=405)
        else: messages.warning(request, "Ação inválida."); return redirect('home:lista_Tarefas')
    try:
        tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)
        usuario_obj = request.user
        if not tarefa.falhou or tarefa.concluida or tarefa.descartada:
             logger.warning(f"Usuário {request.user.email} tentou 'concluir atrasado' (PK {tarefa.pk}) que não está 'falhada'.")
             if is_ajax: return JsonResponse({'error': 'Esta tarefa não pode ser concluída (atrasada).'}, status=403)
             else: messages.error(request, "Esta tarefa não pode ser concluída (atrasada)."); return redirect('home:lista_Tarefas')
        tarefa.descartada = True 
        tarefa.save(update_fields=['descartada', 'data_acao_final']) 
        usuario_obj.tarefas_concluidas_atrasadas_count += 1
        usuario_obj.save(update_fields=['tarefas_concluidas_atrasadas_count'])
        logger.info(f"Tarefa PK {tarefa.pk} marcada como CONCLUÍDA (ATRASADA). Contador: {usuario_obj.tarefas_concluidas_atrasadas_count}")
        if is_ajax:
            return JsonResponse({
                'success': True,
                'concluida': True,
                'xp_ganho': 0,
                'xp_total_usuario': usuario_obj.xp_atual,
                'nivel_usuario': usuario_obj.nivel,
                'xp_proximo_nivel': usuario_obj.xp_proximo_nivel
            })
        else:
            messages.info(request, f'Tarefa "{tarefa.titulo}" foi concluída (sem XP).')
            return redirect('home:lista_Tarefas')
    except Tarefa.DoesNotExist:
        logger.warning(f"Tarefa PK {tarefa_id} não encontrada (para concluir atrasado)!")
        if is_ajax: return JsonResponse({'error': 'Tarefa não encontrada.'}, status=404)
        else: messages.error(request, "Tarefa não encontrada."); return redirect('home:lista_Tarefas')
    except Exception as e:
        logger.exception(f"Erro GERAL concluir_atrasado (pk={tarefa_id}):")
        if is_ajax: return JsonResponse({'error': 'Erro interno.'}, status=500)
        else: messages.error(request, "Erro ao concluir tarefa."); return redirect('home:lista_Tarefas')