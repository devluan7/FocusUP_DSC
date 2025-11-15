# home/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.conquista import UsuarioConquista
from .models.tarefa import Tarefa
from datetime import datetime

# Roda quando salva uma Tarefa, pra dar XP
@receiver(post_save, sender=Tarefa)
def dar_xp_por_tarefa(sender, instance, **kwargs):
    tarefa = instance
    
    # Só dá XP se foi concluída agora (sem data de conclusão)
    if tarefa.concluida and not tarefa.data_conclusao:
        tarefa.usuario.xp_atual += 10
        tarefa.usuario.save(update_fields=['xp_atual'])
        
        # Marca a data pra não dar XP de novo no futuro
        tarefa.data_conclusao = datetime.now()
        tarefa.save(update_fields=['data_conclusao'])


# Roda quando ganha conquista, pra dar XP e checar se upou
@receiver(post_save, sender=UsuarioConquista)
def processar_conquista(sender, instance, created, **kwargs):
    
    # 'created' é pra garantir que só roda na criação
    if created: 
        usuario = instance.usuario
        conquista = instance.conquista
        
        usuario.xp_atual += conquista.xp_points
        
        xp_para_proximo_nivel = usuario.nivel * 100
        
        # Loop pra caso ele upe vários níveis de uma vez
        while usuario.xp_atual >= xp_para_proximo_nivel:
            usuario.nivel += 1
            usuario.xp_atual -= xp_para_proximo_nivel
            xp_para_proximo_nivel = usuario.nivel * 100
            
        usuario.save(update_fields=['xp_atual', 'nivel'])