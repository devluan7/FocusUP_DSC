# home/models/tarefa.py

from django.db import models
from .usuario import Usuario  # Certifique-se que o import de Usuario está correto

class Tarefa(models.Model):
    FREQUENCIA_CHOICES = [
        ('DIARIA', 'Diária'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal')
        # A opção 'JORNADA' foi removida
    ]

    id_Tarefa = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='Tarefas')
    
    # Voltamos o verbose_name para o original
    titulo = models.CharField(max_length=100, verbose_name="Nome do Hábito") 
    
    descricao = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    frequencia = models.CharField(max_length=10, choices=FREQUENCIA_CHOICES, default='DIARIA')
    
    hora_lembrete = models.TimeField(verbose_name="Horário do Lembrete")
    ultimo_lembrete_enviado = models.DateTimeField(blank=True, null=True)

    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    # Os campos 'dificuldade' e 'xp' foram removidos

    def __str__(self):
        # Acessa o nome de usuário através da ForeignKey 'usuario'
        return f'{self.titulo} ({self.usuario.nome_usuario})'