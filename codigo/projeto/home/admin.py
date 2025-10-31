# Register your models here.
from django.contrib import admin
from .models import (
    Usuario,
    Tarefa,
    Conquista,
    UsuarioConquista,
    ItemLoja,
    Compra,
    Amigo,
    Grupo,
    GrupoUsuario,
    GrupoTarefa,
    Notificacao,
    UsuarioFoco
)

# Registra todos os seus models para aparecerem no painel de admin
admin.site.register(Usuario)
admin.site.register(Tarefa)
admin.site.register(Conquista)
admin.site.register(UsuarioConquista)
admin.site.register(ItemLoja)
admin.site.register(Compra)
admin.site.register(Amigo)
admin.site.register(Grupo)
admin.site.register(GrupoUsuario)
admin.site.register(GrupoTarefa)
admin.site.register(Notificacao)
admin.site.register(UsuarioFoco)