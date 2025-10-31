# home/views/amigo_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models.usuario import Usuario
from ..models.amigo import Amigo, PedidoAmizade
from django.contrib.auth import get_user_model

@login_required
def buscar_usuarios(request):
    query = request.GET.get('q', '') 
    resultados = []

    if query:
        resultados = Usuario.objects.filter(
            Q(nome_usuario__icontains=query) | Q(nome__icontains=query)
        ).exclude(pk=request.user.pk)
    contexto = {
        'query': query,
        'resultados': resultados
    }
    return render(request, 'home/amigos/buscar_usuarios.html', contexto)

@login_required
def enviar_pedido_amizade(request, usuario_id):
    para_usuario = get_object_or_404(Usuario, pk=usuario_id)
    de_usuario = request.user

    
    if para_usuario == de_usuario:
        messages.error(request, 'Você não pode adicionar a si mesmo.')
        return redirect('home:buscar_usuarios')
    
    if Amigo.objects.filter(usuario=de_usuario, amigo=para_usuario).exists():
        messages.warning(request, f'Você já é amigo de {para_usuario.nome_usuario}.')
        return redirect('home:buscar_usuarios')

    pedido, created = PedidoAmizade.objects.get_or_create(de_usuario=de_usuario, para_usuario=para_usuario)
    
    if created:
        messages.success(request, f'Pedido de amizade enviado para {para_usuario.nome_usuario}.')
    else:
        messages.info(request, f'Você já enviou um pedido de amizade para {para_usuario.nome_usuario}. Aguarde a resposta.')
    return redirect('home:buscar_usuarios')

@login_required
def listar_pedidos_amizade(request):
    pedidos = PedidoAmizade.objects.filter(para_usuario=request.user, status='pendente')
    return render(request, 'home/amigos/pedidos_amizade.html', {'pedidos': pedidos})

@login_required
def aceitar_pedido_amizade(request, pedido_id):
    pedido = get_object_or_404(PedidoAmizade, pk=pedido_id, para_usuario=request.user)

    if pedido.status == 'pendente':
        pedido.status = 'aceito'
        pedido.save()
        Amigo.objects.create(usuario=pedido.de_usuario, amigo=pedido.para_usuario)
        Amigo.objects.create(usuario=pedido.para_usuario, amigo=pedido.de_usuario)
        messages.success(request, f'Você agora é amigo de {pedido.de_usuario.nome_usuario}!')
    return redirect('home:listar_pedidos_amizade')

@login_required
def recusar_remover_amizade(request, pedido_id): 
    pedido = get_object_or_404(PedidoAmizade, pk=pedido_id, de_usuario=request.user) or get_object_or_404(PedidoAmizade, pk=pedido_id, para_usuario=request.user)  
    Amigo.objects.filter(usuario=pedido.de_usuario, amigo=pedido.para_usuario).delete()
    Amigo.objects.filter(usuario=pedido.para_usuario, amigo=pedido.de_usuario).delete()
    pedido.delete()
    messages.info(request, 'Amizade desfeita/pedido recusado.')   
    return redirect('home:listar_pedidos_amizade')

@login_required
def listar_amigos(request):
    amizades = request.user.amigos.select_related('amigo')
    lista_de_amigos = [amizade.amigo for amizade in amizades]
    return render(request, 'home/amigos/amigos.html', {'amigos': lista_de_amigos})
@login_required
def remover_amigo(request, amigo_username):
    """ Remove a amizade entre o usuário logado e outro usuário """
    if request.method == 'POST':
        try:
            # --- CORREÇÃO AQUI ---
            # Usa o modelo 'Usuario' importado
            amigo = Usuario.objects.get(nome_usuario=amigo_username)

            # Verifica se o amigo encontrado é o próprio usuário (não deveria acontecer pela URL, mas é uma segurança extra)
            if amigo == request.user:
                 messages.error(request, 'Você não pode remover a si mesmo.')
                 return redirect('home:listar_amigos')

            # Tenta encontrar a relação de amizade usando o modelo Amigo
            # (Assumindo que Amigo armazena a relação bidirecionalmente ou tem um jeito de achar)
            # Ou deleta o PedidoAmizade aceito, como no código original

            # ------ Opção 1: Deletar pelo modelo Amigo (se ele existe e representa a amizade) ------
            # Amigo.objects.filter(usuario=request.user, amigo=amigo).delete()
            # Amigo.objects.filter(usuario=amigo, amigo=request.user).delete()

            # ------ Opção 2: Deletar pelo PedidoAmizade aceito (como no código anterior) ------
            pedido_amizade = PedidoAmizade.objects.filter(
                (Q(de_usuario=request.user) & Q(para_usuario=amigo) & Q(status='aceito')) |
                (Q(de_usuario=amigo) & Q(para_usuario=request.user) & Q(status='aceito'))
            ).first()

            if pedido_amizade:
                # Se o PedidoAmizade representa a amizade, deletá-lo pode ser suficiente
                # Ou talvez você precise deletar também as entradas em Amigo
                Amigo.objects.filter(usuario=request.user, amigo=amigo).delete()
                Amigo.objects.filter(usuario=amigo, amigo=request.user).delete()
                pedido_amizade.delete() # Ou apenas marcar como 'removido' se preferir manter histórico
                messages.success(request, f'Você não é mais amigo de {amigo.nome_usuario}.')
            else:
                 # Se não achou PedidoAmizade, talvez a amizade exista só no modelo Amigo? Tente deletar só por ele.
                 deleted_count1, _ = Amigo.objects.filter(usuario=request.user, amigo=amigo).delete()
                 deleted_count2, _ = Amigo.objects.filter(usuario=amigo, amigo=request.user).delete()
                 if deleted_count1 > 0 or deleted_count2 > 0:
                      messages.success(request, f'Você não é mais amigo de {amigo.nome_usuario}.')
                 else:
                      messages.error(request, 'Não foi possível encontrar a amizade para remover.')


        # --- CORREÇÃO AQUI ---
        # Usa o modelo 'Usuario' importado
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao remover a amizade: {e}')

        return redirect('home:listar_amigos')
    else:
        messages.warning(request, 'Ação não permitida.')
        return redirect('home:listar_amigos')
        