# home/models/usuario.py


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    ofensiva = models.IntegerField(null=True, blank=True, verbose_name='Poder de ataque do avatar')
    avatar = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "nome_usuario"]

    def __str__(self):
        return self.email