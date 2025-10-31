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
    
    # --- URL renomeada para Perfil de Focos ---
    path('meu-perfil/focos/', usuario_views.gerenciar_meu_perfil_focos, name='meu_perfil_focos'), 
    
    # --- NOVA URL ADICIONADA ---
    path('meu-perfil/editar/', usuario_views.editar_perfil, name='editar_perfil'),
    # --------------------------
    
    path('termos/', usuario_views.termos, name='termos'),

    # --- URL DE RESGATE DE FOCO ---
    path('resgatar-foco/', usuario_views.resgatar_foco, name='resgatar_foco'),
    # ------------------------------------
    
    # --- URLs de Tarefas ---
    path('Tarefas/', tarefa_views.lista_Tarefas, name='lista_Tarefas'),
    path('Tarefas/adicionar/', tarefa_views.adicionar_Tarefas, name='adicionar_Tarefas'),
    path('tarefas/<int:tarefa_id>/concluir/', tarefa_views.concluir_tarefa, name='concluir_tarefa'),

    # --- URLs da IA (REMOVIDAS POIS A LÓGICA ESTÁ EM 'adicionar_Tarefas') ---
    # path('Tarefas/gerar-ia/', tarefa_views.gerar_sugestao_ia_view, name='gerar_sugestao_ia'),
    # path('Tarefas/salvar-ia/', tarefa_views.salvar_sugestao_ia_view, name='salvar_sugestao_ia'),
    # ---------------------------------

    # --- URLs para sistema de amizade ---
    path('usuarios/buscar/', amigo_views.buscar_usuarios, name='buscar_usuarios'),
    path('amigos/', amigo_views.listar_amigos, name='listar_amigos'),
    path('amigos/pedidos/', amigo_views.listar_pedidos_amizade, name='listar_pedidos_amizade'),
    path('amigos/enviar_pedido/<str:usuario_id>/', amigo_views.enviar_pedido_amizade, name='enviar_pedido_amizade'),
    path('amigos/aceitar/<int:pedido_id>/', amigo_views.aceitar_pedido_amizade, name='aceitar_pedido_amizade'),
    path('amigos/recusar/<int:pedido_id>/', amigo_views.recusar_remover_amizade, name='recusar_remover_amizade'),


    # --- URLs PARA REDEFINIÇÃO DE SENHA ---
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(
             template_name="home/reset_senha/password_reset_form.html",
             success_url=reverse_lazy('home:password_reset_done')
         ), 
         name='password_reset'),

    path('reset_password/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name="home/reset_senha/password_reset_done.html"
         ), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="home/reset_senha/password_reset_confirm.html",
             success_url=reverse_lazy('home:password_reset_complete') 
         ), 
         name='password_reset_confirm'),

    path('reset_password/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="home/reset_senha/password_reset_complete.html"
         ), 
         name='password_reset_complete'),
]