# home/context_processors.py
# Verifique se o caminho para PedidoAmizade está correto aqui!
from .models.amigo import PedidoAmizade # Ou from .models.pedido_amizade import PedidoAmizade

def pending_requests_count(request):
    """
    Retorna a contagem de pedidos de amizade pendentes para o usuário logado.
    """
    count = 0
    if request.user.is_authenticated:
        count = PedidoAmizade.objects.filter(
            para_usuario=request.user,
            status='pendente' 
        ).count()
    return {'pending_requests_count': count}