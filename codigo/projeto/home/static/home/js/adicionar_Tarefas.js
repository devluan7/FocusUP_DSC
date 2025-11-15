// static/home/js/adicionar_Tarefas.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("adicionar_Tarefas.js Carregado! (v3 - Gerenciador de Recorrência)");

    const listaRecorrencia = document.getElementById('lista-recorrencia');
    const container = document.querySelector('.container-add-tarefa');
    
    // Pega as URLs e o Token do HTML
    const ajaxUrlSalvar = container ? container.dataset.ajaxUrlSalvarRecorrencia : null;
    const csrftoken = container ? container.dataset.csrfToken : null;

    if (!listaRecorrencia) {
        console.log("Lista de recorrência não encontrada (normal se não houver tarefas).");
        return;
    }
    if (!ajaxUrlSalvar || !csrftoken) {
        console.error("ERRO CRÍTICO: URL de salvar recorrência ou CSRF Token não encontrados no .container-add-tarefa");
        return;
    }


    // --- LÓGICA 1: ABRIR E FECHAR O DROPDOWN ---

    listaRecorrencia.addEventListener('click', function(event) {
        // 1. O usuário clicou no BOTÃO "Definir recorrência"?
        const botaoToggle = event.target.closest('[data-action="toggle-recorrencia"]');
        if (botaoToggle) {
            event.preventDefault();
            const dropdown = botaoToggle.closest('.dropdown-recorrencia');
            
            // Fecha todos os outros menus que possam estar abertos
            document.querySelectorAll('.dropdown-recorrencia.is-open').forEach(openDropdown => {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('is-open');
                }
            });

            // Abre ou fecha o menu clicado
            dropdown.classList.toggle('is-open');
        }
    });

    // Fecha o menu se o usuário clicar em qualquer lugar fora dele
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown-recorrencia')) {
            document.querySelectorAll('.dropdown-recorrencia.is-open').forEach(openDropdown => {
                openDropdown.classList.remove('is-open');
            });
        }
    });


    // --- LÓGICA 2: SALVAR O CHECKBOX (AJAX) ---

    listaRecorrencia.addEventListener('change', function(event) {
        // O usuário marcou/desmarcou um CHECKBOX?
        const checkbox = event.target.closest('.recorrencia-dropdown-menu input[type="checkbox"]');
        if (checkbox) {
            const dropdownMenu = checkbox.closest('.recorrencia-dropdown-menu');
            const botao = dropdownMenu.previousElementSibling;
            const itemLi = checkbox.closest('li.item-recorrencia');
            const tarefaId = itemLi.dataset.tarefaId;
            const dia = checkbox.name; // Ex: 'dom', 'seg'
            const status = checkbox.checked; // Ex: true, false

            // Atualiza o texto do botão (lógica visual primeiro, para ser rápido)
            atualizarTextoBotao(botao, dropdownMenu);
            
            // Chama a função para salvar no backend
            salvarRecorrencia(tarefaId, dia, status, botao);
        }
    });

    /**
     * Atualiza o texto do botão com base nos checkboxes marcados
     */
    function atualizarTextoBotao(botao, dropdownMenu) {
        const inputsMarcados = dropdownMenu.querySelectorAll('input:checked');
        let diasSelecionados = [];
        inputsMarcados.forEach(input => {
            diasSelecionados.push(input.dataset.dia); // "Seg", "Ter", etc.
        });

        if (diasSelecionados.length === 0) {
            botao.textContent = 'Definir recorrência';
            botao.classList.add('botao-recorrencia-vazio'); // (Classe do CSS)
        } else if (diasSelecionados.length === 7) {
            botao.textContent = 'Todos os dias';
            botao.classList.remove('botao-recorrencia-vazio');
        } else {
            botao.textContent = diasSelecionados.join(', ');
            botao.classList.remove('botao-recorrencia-vazio');
        }
    }

    /**
     * Envia a mudança do checkbox para o servidor via AJAX (Fetch)
     */
    async function salvarRecorrencia(tarefaId, dia, status, botao) {
        console.log(`Salvando... Tarefa ${tarefaId}, Dia: ${dia}, Status: ${status}`);
        
        // Adiciona um efeitinho de "loading" no botão
        botao.style.opacity = '0.5';
        botao.disabled = true; 

        try {
            const response = await fetch(ajaxUrlSalvar, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    tarefa_id: tarefaId,
                    dia: dia,
                    status: status
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Erro de rede");
            }

            const data = await response.json();
            
            if (data.success) {
                console.log("Recorrência salva com sucesso.");
                // Atualiza o texto do botão com a string final vinda do backend
                // (Isso garante que "Todos os dias" etc. está correto)
                botao.textContent = data.novo_texto;
                
                // Remove a classe de "vazio" se o backend não retornar o texto padrão
                if (data.novo_texto !== "Definir recorrência") {
                     botao.classList.remove('botao-recorrencia-vazio');
                } else {
                     botao.classList.add('botao-recorrencia-vazio');
                }

            } else {
                throw new Error(data.error || "O servidor recusou a mudança.");
            }

        } catch (error) {
            console.error("Erro ao salvar recorrência:", error);
            alert(`Erro ao salvar: ${error.message}. A página será recarregada.`);
            location.reload(); // Recarrega a página em caso de erro
        } finally {
            // Remove o efeitinho de "loading"
            botao.style.opacity = '1';
            botao.disabled = false;
        }
    }

});