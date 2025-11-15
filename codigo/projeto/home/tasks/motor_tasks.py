# home/tasks/motor_tasks.py

import logging
import random
from datetime import datetime, time 
from django.utils import timezone
from ..models.tarefa import Tarefa
from ..models.usuario import Usuario 

logger = logging.getLogger(__name__)

DIAS_DA_SEMANA_MAP = {
    0: 'recorrente_seg', 1: 'recorrente_ter', 2: 'recorrente_qua',
    3: 'recorrente_qui', 4: 'recorrente_sex', 5: 'recorrente_sab',
    6: 'recorrente_dom',
}

def processar_slots_diarios(usuario: Usuario):
    
    logger.info(f"Processando 'motor' para: {usuario.email}")
    
    HORA_CORTE = usuario.HORA_CORTE_RESET
    agora = timezone.localtime(timezone.now())
    inicio_dia_de_jogo_atual = usuario.get_inicio_dia_de_jogo_atual()

    
    tarefas_para_falhar = Tarefa.objects.filter(
        usuario=usuario,
        tipo_tarefa__in=['PESSOAL', 'DIARIA'], 
        concluida=False,
        falhou=False,
        descartada=False,
        data_criacao__lt=inicio_dia_de_jogo_atual 
    )
    
    count_falhadas = tarefas_para_falhar.update(
        falhou=True,
        xp=0 
    )
    
    if count_falhadas > 0:
        logger.info(f"RESET: {count_falhadas} tarefas antigas marcadas como 'Falhou' para {usuario.email}.")


    slots_usados_hoje = usuario.resetar_slots_tarefas_pessoais()
    
    if slots_usados_hoje == 0:
        logger.info(f"HORA DO SORTEIO para {usuario.email}...")
        
        dia_para_buscar = None
        
        if agora.time() >= HORA_CORTE:
            logger.info(f"Corte ({HORA_CORTE}) já passou. Gerando tarefas de AMANHÃ.")
            amanha = agora + timezone.timedelta(days=1)
            dia_para_buscar = amanha.weekday()
        else:
            logger.info(f"Corte ({HORA_CORTE}) ainda não passou. Gerando tarefas de HOJE.")
            dia_para_buscar = agora.weekday()

        campo_dia_de_hoje = DIAS_DA_SEMANA_MAP.get(dia_para_buscar)
        
        if not campo_dia_de_hoje:
            logger.error(f"Não foi possível encontrar o dia da semana para {dia_para_buscar}")
            return 

        templates_para_hoje = Tarefa.objects.filter(
            usuario=usuario,
            tipo_tarefa='TEMPLATE_PESSOAL',
            **{campo_dia_de_hoje: True}
        )
        
        templates_list = list(templates_para_hoje)
        logger.info(f"Encontrados {len(templates_list)} templates para {usuario.email} para o dia '{campo_dia_de_hoje}'.")

        limite_slots = Usuario.LIMITE_SLOTS_PESSOAIS
        k = min(len(templates_list), limite_slots) 
        
        if k > 0:
            templates_sorteados = random.sample(templates_list, k=k)
            logger.info(f"Sorteando {k} tarefas para {usuario.email}...")
            
            novas_tarefas_criadas = []
            
            for template in templates_sorteados:
                nova_tarefa_pessoal = Tarefa.objects.create(
                    usuario=usuario,
                    tipo_tarefa='PESSOAL', 
                    titulo=template.titulo,
                    descricao=template.descricao,
                    hora_lembrete=template.hora_lembrete,
                    xp=template.xp_original or 10, 
                    xp_original=template.xp_original or 10,
                    concluida=False,
                    falhou=False
                )
                novas_tarefas_criadas.append(nova_tarefa_pessoal)
            
            usuario.slots_tarefas_pessoais_usados = len(novas_tarefas_criadas)
            usuario.save(update_fields=['slots_tarefas_pessoais_usados'])
            logger.info(f"{len(novas_tarefas_criadas)} tarefas PESSOAIS criadas para {usuario.email}.")

        else:
            logger.info(f"Nenhum template de tarefa pessoal para sortear para {usuario.email}.")
    
    else:
        logger.info(f"Slots para {usuario.email} já foram processados ({slots_usados_hoje}). Pulando Sorteio.")