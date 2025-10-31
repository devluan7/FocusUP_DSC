# home/urls.py

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
# Importe todos os seus arquivos de views que são usados aqui
from .views import usuario_views, tarefa_views, amigo_views 
# Não precisamos importar views2 aqui, pois a view está em usuario_views agora

app_name = 'home' 

urlpatterns = [
    
    # --- URLs de Usuario ---
    path('', usuario_views.index, name='index'),
    path('home/', usuario_views.home, name='home'),
    path('login/', usuario_views.login_view, name='login'),
    path('logout/', usuario_views.logout_view, name='logout'),
    path('cadastro/', usuario_views.cadastro, name='cadastro'),
    
    # <-- ADICIONE ISSO: A nova URL para a página de perfil/focos
    path('meu-perfil/', usuario_views.gerenciar_meu_perfil, name='meu_perfil'), 
    
    path('termos/', usuario_views.termos, name='termos'),
    
    # --- URLs de Tarefas ---
    path('Tarefas/', tarefa_views.lista_Tarefas, name='lista_Tarefas'),
    path('Tarefas/adicionar/', tarefa_views.adicionar_Tarefas, name='adicionar_Tarefas'),
    path('tarefas/<int:tarefa_id>/concluir/', tarefa_views.concluir_tarefa, name='concluir_tarefa'),

    # --- URLs para sistema de amizade ---
    path('usuarios/buscar/', amigo_views.buscar_usuarios, name='buscar_usuarios'),
    path('amigos/', amigo_views.listar_amigos, name='listar_amigos'),
    path('amigos/pedidos/', amigo_views.listar_pedidos_amizade, name='listar_pedidos_amizade'),
    path('amigos/enviar_pedido/<str:usuario_id>/', amigo_views.enviar_pedido_amizade, name='enviar_pedido_amizade'),
    path('amigos/aceitar/<int:pedido_id>/', amigo_views.aceitar_pedido_amizade, name='aceitar_pedido_amizade'),
    path('amigos/recusar/<int:pedido_id>/', amigo_views.recusar_remover_amizade, name='recusar_remover_amizade'),
    path('amigos/remover/<str:amigo_username>/', amigo_views.remover_amigo, name='remover_amigo'),

]