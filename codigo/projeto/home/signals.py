# home/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.conquista import UsuarioConquista
from .models.tarefa import Tarefa # <--- ADICIONE ESTA IMPORTAÇÃO
from datetime import datetime     # <--- ADICIONE ESTA IMPORTAÇÃO

# ==========================================================
# SIGNAL DE XP POR TAREFA (O QUE ESTAVA FALTANDO)
# ==========================================================
@receiver(post_save, sender=Tarefa)
def dar_xp_por_tarefa(sender, instance, **kwargs):
    tarefa = instance
    
    # A regra: dá XP se a tarefa está 'concluida' E ainda não tem uma 'data_conclusao'
    if tarefa.concluida and not tarefa.data_conclusao:
        # Adiciona 10 de XP (ou o valor que você preferir)
        tarefa.usuario.xp_atual += 10
        tarefa.usuario.save(update_fields=['xp_atual'])
        
        # Define a data de conclusão para não dar XP de novo
        tarefa.data_conclusao = datetime.now()
        tarefa.save(update_fields=['data_conclusao'])

        # Opcional: Chamar a verificação de nível aqui também
        # (seu signal de conquista já faz isso, mas pode ser bom ter aqui também)


# ==========================================================
# SIGNAL DE XP POR CONQUISTA (O QUE VOCÊ JÁ TINHA)
# ==========================================================
@receiver(post_save, sender=UsuarioConquista)
def processar_conquista(sender, instance, created, **kwargs):
    """
    Este signal é acionado sempre que um UsuarioConquista é criado.
    Ele adiciona XP e verifica se o usuário subiu de nível.
    """
    if created:
        usuario = instance.usuario
        conquista = instance.conquista
        usuario.xp_atual += conquista.xp_points
        
        xp_para_proximo_nivel = usuario.nivel * 100
        
        while usuario.xp_atual >= xp_para_proximo_nivel:
            usuario.nivel += 1
            usuario.xp_atual -= xp_para_proximo_nivel
            xp_para_proximo_nivel = usuario.nivel * 100
        
        usuario.save(update_fields=['xp_atual', 'nivel'])