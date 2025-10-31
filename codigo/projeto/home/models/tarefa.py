# home/models/tarefa.py

from django.db import models
from .usuario import Usuario  # Certifique-se que o import de Usuario está correto
from django.utils import timezone # <-- ADICIONE ESTE IMPORT

class Tarefa(models.Model):
    FREQUENCIA_CHOICES = [
        ('DIARIA', 'Diária'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal')
    ]

    id_Tarefa = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='Tarefas')
    
    titulo = models.CharField(max_length=100, verbose_name="Nome do Hábito") 
    
    descricao = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    frequencia = models.CharField(max_length=10, choices=FREQUENCIA_CHOICES, default='DIARIA')
    
    # Baseado em erros anteriores, este campo NÃO PODE ser nulo
    hora_lembrete = models.TimeField(verbose_name="Horário do Lembrete") 
    ultimo_lembrete_enviado = models.DateTimeField(blank=True, null=True)

    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    # --- CAMPO DE XP ADICIONADO DE VOLTA ---
    # Define um valor padrão (10 XP) para tarefas criadas manualmente.
    # A IA poderá definir valores diferentes (30, 60, etc.) quando salvar.
    xp = models.IntegerField(default=10, verbose_name="XP da Tarefa")
    # ------------------------------------

    def __str__(self):
        # Tenta pegar 'nome_usuario', se não existir, usa 'email'
        nome_display = getattr(self.usuario, 'nome_usuario', self.usuario.email)
        return f'{self.titulo} ({nome_display})'

    # --- MÉTODO SAVE ADICIONADO (BOA PRÁTICA) ---
    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para atualizar a data de conclusão 
        automaticamente com base no status 'concluida'.
        """
        if self.concluida and not self.data_conclusao:
            # Se a tarefa está sendo marcada como concluída e não tem data, defina agora.
            self.data_conclusao = timezone.now()
        elif not self.concluida:
            # Se a tarefa está sendo marcada como NÃO concluída (desmarcada), limpe a data.
            self.data_conclusao = None
        
        super().save(*args, **kwargs) # Chama o método save original do Django
    # --------------------------------------