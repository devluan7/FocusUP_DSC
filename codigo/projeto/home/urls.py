# home/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import usuario_views, tarefa_views, amigo_views

app_name = 'home'

urlpatterns = [
    # URLs de autenticação e páginas principais
    path('', usuario_views.index, name='index'),
    path('home/', usuario_views.home, name='home'),
    path('login/', usuario_views.login_view, name='login'),
    path('logout/', usuario_views.logout_view, name='logout'),
    path('cadastro/', usuario_views.cadastro, name='cadastro'),

    # URLs do perfil do usuário
    path('meu-perfil/', usuario_views.gerenciar_meu_perfil, name='meu_perfil'),
    path('meu-perfil/editar/', usuario_views.editar_perfil, name='editar_perfil'),

    path('termos/', usuario_views.termos, name='termos'),

    # URL para o usuário resgatar a pontuação (Foco)
    path('resgatar-foco/', usuario_views.resgatar_foco, name='resgatar_foco'),

    # URLs para gerenciar as tarefas
    path('Tarefas/', tarefa_views.lista_Tarefas, name='lista_Tarefas'),
    path('Tarefas/adicionar/', tarefa_views.adicionar_Tarefas, name='adicionar_Tarefas'),
    path('tarefas/<int:tarefa_id>/concluir/', tarefa_views.concluir_tarefa, name='concluir_tarefa'),
    path('tarefas/salvar-recorrencia/', tarefa_views.salvar_recorrencia, name='salvar_recorrencia'),
    path('tarefas/<int:tarefa_id>/descartar/', tarefa_views.descartar_tarefa, name='descartar_tarefa'),

    # Essa aqui é o 'jeitinho' pra concluir tarefa atrasada
    path('tarefas/<int:tarefa_id>/concluir-atrasado/', tarefa_views.concluir_atrasado, name='concluir_atrasado'),

    # URLs do sistema de amizade
    path('usuarios/buscar/', amigo_views.buscar_usuarios, name='buscar_usuarios'),
    path('amigos/', amigo_views.listar_amigos, name='listar_amigos'),
    path('amigos/pedidos/', amigo_views.listar_pedidos_amizade, name='listar_pedidos_amizade'),
    path('amigos/enviar_pedido/<str:usuario_id>/', amigo_views.enviar_pedido_amizade, name='enviar_pedido_amizade'),
    path('amigos/aceitar/<int:pedido_id>/', amigo_views.aceitar_pedido_amizade, name='aceitar_pedido_amizade'),
    path('amigos/recusar/<int:pedido_id>/', amigo_views.recusar_remover_amizade, name='recusar_remover_amizade'),
    path('amigos/remover/<str:amigo_username>/', amigo_views.remover_amigo, name='remover_amigo')
]