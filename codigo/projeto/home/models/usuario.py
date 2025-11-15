from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone 
from datetime import date, time 

import logging
logger = logging.getLogger(__name__)


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, nome_usuario, senha=None, **extra_fields):
        if not email:
            raise ValueError("O usuário precisa de um email")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nome=nome,
            nome_usuario=nome_usuario,
            **extra_fields
        )
        user.set_password(senha)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nome, nome_usuario, senha=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, nome, nome_usuario, senha, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    sexo_choices =[
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    email = models.EmailField(primary_key=True, unique=True, verbose_name='E-mail do usuário')
    nome = models.CharField(max_length=100, verbose_name='Nome completo do usuário')
    nome_usuario = models.CharField(max_length=50, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=sexo_choices, null=True, blank=True, verbose_name='Sexo (M/F/O)')
    
    foco = models.CharField(max_length=50, null=True, blank=True, verbose_name='Área de foco')
    
    nivel = models.IntegerField(default=1)
    xp_atual = models.IntegerField(default=0)
    xp_proximo_nivel = models.IntegerField(default=100, verbose_name='XP para o próximo nível')
    
    ofensiva = models.IntegerField(null=True, blank=True, verbose_name='Poder de ataque do avatar')
    avatar = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    dias_foco = models.IntegerField(default=0, verbose_name='Dias de Foco (Streak)')
    ultimo_resgate_foco = models.DateTimeField(null=True, blank=True, verbose_name='Último Resgate de Foco')
    
    slots_tarefas_pessoais_usados = models.IntegerField(default=0, verbose_name="Slots de tarefas pessoais usados hoje")
    
    data_reset_slots = models.DateField(default=date.today, verbose_name="Último dia que os slots foram resetados")
    
    tarefas_concluidas_prazo_count = models.IntegerField(default=0, verbose_name="Contador de tarefas concluídas (no prazo)")
    tarefas_concluidas_atrasadas_count = models.IntegerField(default=0, verbose_name="Contador de tarefas concluídas (atrasadas)")
    tarefas_descartadas_count = models.IntegerField(default=0, verbose_name="Contador de tarefas descartadas")
    
    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "nome_usuario"]

    XP_BASE_PARA_NIVEL_2 = 100
    XP_MULTIPLICADOR = 1.5 
    LIMITE_SLOTS_PESSOAIS = 3
    
    # Hora que o dia vira no jogo (tipo 18:57)
    HORA_CORTE_RESET = time(18, 57, 0) 

    def adicionar_xp(self, quantidade):
        if quantidade <= 0:
            return False
        self.xp_atual += quantidade
        logger.debug(f"Usuário {self.email} ganhou {quantidade} XP. Total agora: {self.xp_atual}")
        self.save(update_fields=['xp_atual'])
        return self.verificar_level_up()

    def verificar_level_up(self):
        upou = False 
        # Loop pra garantir que ele suba quantos níveis precisar de uma vez
        while self.xp_atual >= self.xp_proximo_nivel:
            upou = True
            self.nivel += 1
            xp_excedente = self.xp_atual - self.xp_proximo_nivel
            novo_xp_necessario = int(
                self.XP_BASE_PARA_NIVEL_2 * (self.XP_MULTIPLICADOR ** (self.nivel - 1))
            )
            self.xp_atual = xp_excedente
            self.xp_proximo_nivel = novo_xp_necessario
            self.save(update_fields=['xp_atual', 'xp_proximo_nivel', 'nivel'])
            logger.info(f"Usuário {self.email} UPOU! Nível: {self.nivel}. XP atual: {self.xp_atual}. Próximo nível: {self.xp_proximo_nivel} XP.")
        return upou
        
    def get_inicio_dia_de_jogo_atual(self):
        # Descobre quando começou o "dia" atual do jogo, baseado na hora de corte
        agora = timezone.localtime(timezone.now())
        hora_corte_int = self.HORA_CORTE_RESET.hour
        minuto_corte_int = self.HORA_CORTE_RESET.minute
        
        if agora.time() < self.HORA_CORTE_RESET:
            inicio_dia = agora.replace(hour=hora_corte_int, minute=minuto_corte_int, second=0, microsecond=0) - timezone.timedelta(days=1)
        else:
            inicio_dia = agora.replace(hour=hora_corte_int, minute=minuto_corte_int, second=0, microsecond=0)
        
        return inicio_dia

    def resetar_slots_tarefas_pessoais(self):
        # Zera os slots se o dia do jogo mudou
        data_do_dia_de_jogo_atual = self.get_inicio_dia_de_jogo_atual().date()
        
        if self.data_reset_slots < data_do_dia_de_jogo_atual:
            logger.info(f"Resetando slots de tarefas para o usuário {self.email}. Data antiga: {self.data_reset_slots}, Data nova: {data_do_dia_de_jogo_atual}")
            self.slots_tarefas_pessoais_usados = 0
            self.data_reset_slots = data_do_dia_de_jogo_atual 
            self.save(update_fields=['slots_tarefas_pessoais_usados', 'data_reset_slots'])
        
        return self.slots_tarefas_pessoais_usados

    def __str__(self):
        return self.email