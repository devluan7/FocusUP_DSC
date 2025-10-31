# home/models/usuario.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --- IMPORT NECESSÁRIO PARA O LOGGER ---
import logging
logger = logging.getLogger(__name__)
# -------------------------------------


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
    
    # --- CAMPOS DE NÍVEL E XP ---
    nivel = models.IntegerField(default=1)
    xp_atual = models.IntegerField(default=0)
    # --- NOVO CAMPO ---
    xp_proximo_nivel = models.IntegerField(default=100, verbose_name='XP para o próximo nível')
    # -------------------
    
    ofensiva = models.IntegerField(null=True, blank=True, verbose_name='Poder de ataque do avatar')
    avatar = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # --- CAMPOS PARA O FOCO DIÁRIO ---
    dias_foco = models.IntegerField(default=0, verbose_name='Dias de Foco (Streak)')
    ultimo_resgate_foco = models.DateTimeField(null=True, blank=True, verbose_name='Último Resgate de Foco')
    # --------------------------------------

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "nome_usuario"]

    # --- CONSTANTES E MÉTODOS DE NÍVEL (NOVOS) ---
    XP_BASE_PARA_NIVEL_2 = 100
    XP_MULTIPLICADOR = 1.5 # 50% a mais de XP por nível

    def adicionar_xp(self, quantidade):
        """
        Adiciona XP ao usuário e chama a verificação de level up.
        """
        if quantidade <= 0:
            return False
            
        self.xp_atual += quantidade
        logger.debug(f"Usuário {self.email} ganhou {quantidade} XP. Total agora: {self.xp_atual}")
        
        # Chama a função de verificação de level up
        return self.verificar_level_up()

    def verificar_level_up(self):
        """
        Verifica se o XP atual é suficiente para subir de nível.
        Usa um 'while' para o caso de o usuário ganhar XP para vários níveis.
        Retorna True se o usuário subiu de nível, False caso contrário.
        """
        upou = False 
        
        while self.xp_atual >= self.xp_proximo_nivel:
            upou = True
            
            # 1. Subiu de nível!
            self.nivel += 1
            
            # 2. Deduz o XP que foi "gasto" para subir
            xp_excedente = self.xp_atual - self.xp_proximo_nivel
            
            # 3. Calcula o novo XP necessário para o *próximo* nível
            novo_xp_necessario = int(
                self.XP_BASE_PARA_NIVEL_2 * (self.XP_MULTIPLICADOR ** (self.nivel - 1))
            )
            
            # 4. Atualiza os campos
            self.xp_atual = xp_excedente
            self.xp_proximo_nivel = novo_xp_necessario
            
            logger.info(f"Usuário {self.email} UPOU! Nível: {self.nivel}. XP atual: {self.xp_atual}. Próximo nível: {self.xp_proximo_nivel} XP.")

        return upou
    # --- FIM DOS MÉTODOS DE NÍVEL ---

    def __str__(self):
        return self.email