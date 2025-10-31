# home/views/tarefa_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..forms import TarefaForm
from ..models.tarefa import Tarefa 
from ..models.conquista import Conquista, UsuarioConquista


def verificar_e_conceder_conquistas_de_tarefas(usuario):
    
    tarefas_concluidas_count = Tarefa.objects.filter(usuario=usuario, concluida=True).count()

    conquistas_por_tarefas = {
        "Iniciante Esforçado": 1,
        "Mestre das 5 Tarefas": 5,
        "Produtividade em Pessoa": 10,
        "Lenda das 25 Tarefas": 25,
    }

    
    for nome_conquista, criterio_count in conquistas_por_tarefas.items():
        if tarefas_concluidas_count >= criterio_count:        
            possui_conquista = UsuarioConquista.objects.filter(usuario=usuario, conquista__nome=nome_conquista).exists()

            if not possui_conquista:                
                conquista, created = Conquista.objects.get_or_create(
                    nome=nome_conquista,
                    defaults={'criterio': f'Concluir {criterio_count} tarefas.', 'xp_points': criterio_count * 10} 
                )            
                UsuarioConquista.objects.create(usuario=usuario, conquista=conquista)
                print(f"Conquista '{nome_conquista}' concedida para {usuario.nome_usuario}!")

@login_required
def lista_Tarefas(request): 
    tarefas_do_usuario = Tarefa.objects.filter(usuario=request.user).order_by('data_criacao')
    contexto = {
        'tarefas': tarefas_do_usuario
    }
    return render(request, 'home/tarefas/lista_Tarefas.html', contexto)


@login_required
def adicionar_Tarefas(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            nova_tarefa = form.save(commit=False)
            nova_tarefa.usuario = request.user
            nova_tarefa.save()
            verificar_e_conceder_conquistas_de_tarefas(request.user)
            
            return redirect('home:lista_Tarefas')
    else:
        form = TarefaForm()
    
    return render(request, 'home/tarefas/adicionar_Tarefas.html', {'form': form})


@login_required 
def concluir_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, pk=tarefa_id, usuario=request.user)

    if request.method == 'POST':
        era_concluida_antes = tarefa.concluida

        tarefa.concluida = not tarefa.concluida
        tarefa.save()

        if not era_concluida_antes and tarefa.concluida:
            verificar_e_conceder_conquistas_de_tarefas(request.user)
    
    return redirect('home:lista_Tarefas')