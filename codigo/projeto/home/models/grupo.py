from django.db import models
from .usuario import Usuario

class Grupo(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    # O líder é um usuário, mas com um nome diferente pra não confundir
    lider = models.ForeignKey(Usuario, related_name='lider_de_grupo', on_delete=models.CASCADE)
    # Aqui conecta com a tabela 'GrupoUsuario' pra saber quem tá no grupo
    membros = models.ManyToManyField(Usuario, through='GrupoUsuario', related_name='grupos')

    def __str__(self):
        return self.nome

class GrupoUsuario(models.Model):
    # Essa tabela serve pra ligar o usuário ao grupo e saber quando ele entrou
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_entrada = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('grupo', 'usuario')
        verbose_name = 'Membro de Grupo'
        verbose_name_plural = 'Membros de Grupos'
        
    def __str__(self):
        return f'{self.usuario.nome_usuario} em {self.grupo.nome}'


class GrupoTarefa(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
        ('atrasada', 'Atrasada'),
    ]

    id_grupo_tarefa = models.AutoField(primary_key=True)
    # A tarefa pertence ao grupo, não a um usuário só
    grupo = models.ForeignKey(Grupo, related_name='tarefas_grupo', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    class Meta:
        verbose_name = 'Tarefa de Grupo'
        verbose_name_plural = 'Tarefas de Grupos'

    def __str__(self):
        return f'Tarefa "{self.titulo}" do grupo "{self.grupo.nome}"'