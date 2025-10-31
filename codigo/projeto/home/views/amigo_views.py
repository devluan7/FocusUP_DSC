# home/views/amigo_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models.usuario import Usuario
from ..models.amigo import Amigo, PedidoAmizade

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
    return render(request, 'home/amigoa/pedidos_amizade.html', {'pedidos': pedidos})

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