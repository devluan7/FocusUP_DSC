// static/home/js/lista_tarefas_ai.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("lista_tarefas_ai.js Carregado! v13 (Correção 'Adicionando...' com Reload)"); // Versão atualizada

    // --- Elementos, URLs, Token ---
    const seletorFocoIA = document.getElementById('seletor-foco-ia-lista');
    const botaoGerarIA = document.getElementById('botao-gerar-ia-lista');
    const areaSugestao = document.getElementById('area-sugestao-lista');
    const feedbackIA = document.getElementById('feedback-ia-lista');
    const botaoAceitar = document.getElementById('botao-aceitar-lista');
    const botaoDispensar = document.getElementById('botao-dispensar-lista');
    const listaTarefasUL = document.getElementById('lista-tarefas-ul');
    let itemListaVazia = document.getElementById('lista-tarefas-vazia');
    const container = document.querySelector('.container-tarefas');
    
    // --- Elementos (Slots) ---
    const contadorSlotsVisual = document.getElementById('contador-slots-visual');
    const areaAdicionarTarefas = document.getElementById('area-adicionar-tarefas');
    const limiteSlotsMensagem = document.getElementById('limite-slots-mensagem');
    
    const ajaxUrlGerar = container ? container.dataset.ajaxUrlGerar : null;
    const ajaxUrlSalvar = container ? container.dataset.ajaxUrlSalvar : null;
    const csrftoken = container ? container.dataset.csrfToken : null;

    // --- Variáveis (Slots) ---
    let slotsUsados = container ? parseInt(container.dataset.slotsUsados, 10) : 0;
    let slotsLimite = container ? parseInt(container.dataset.slotsLimite, 10) : 3;

    let sugestaoAtual = null; 

    // --- Verificações Iniciais ---
    if (!listaTarefasUL || !container) {
        console.error("ERRO: Elementos essenciais da PÁGINA não encontrados.");
        return;
    }
    console.log(`Slots Iniciais: ${slotsUsados} / ${slotsLimite}`);

    // --- FUNÇÃO "LER MAIS" ---
    const MAX_CHARS_DESCRIPTION = 100; 
    function applyReadMore(parentElement) {
        // (Seu código ... sem mudanças)
        if (!parentElement) { return; }
        const descriptions = parentElement.querySelectorAll('.task-description-full[data-fulltext]');
        descriptions.forEach((desc) => {
            const fullText = desc.dataset.fulltext;
            desc.innerHTML = ''; 
            if (fullText.length > MAX_CHARS_DESCRIPTION) {
                const shortText = fullText.substring(0, MAX_CHARS_DESCRIPTION) + "...";
                const textSpan = document.createElement('span');
                textSpan.className = 'description-text'; 
                textSpan.textContent = shortText;
                const readMoreLink = document.createElement('button');
                readMoreLink.textContent = " Ler Mais";
                readMoreLink.className = 'read-more-link';
                readMoreLink.type = 'button'; 
                desc.appendChild(textSpan);
                desc.appendChild(readMoreLink);
                desc.classList.add('truncated'); 
                readMoreLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (desc.classList.contains('truncated')) {
                        textSpan.textContent = fullText; 
                        readMoreLink.textContent = " Ler Menos"; 
                        desc.classList.remove('truncated');
                    } else {
                        textSpan.textContent = shortText; 
                        readMoreLink.textContent = " Ler Mais"; 
                        desc.classList.add('truncated');
                    }
                });
            } else {
                desc.textContent = fullText;
                desc.classList.remove('truncated');
            }
        });
    }
    
    // --- Funções de Controle de Slots e UI ---
    function atualizarContadorSlots() {
        // (Seu código ... sem mudanças)
        if (contadorSlotsVisual) {
            contadorSlotsVisual.textContent = `${slotsUsados} / ${slotsLimite}`;
        }
        if (slotsUsados >= slotsLimite) {
            if (areaAdicionarTarefas) areaAdicionarTarefas.style.display = 'none';
            if (limiteSlotsMensagem) limiteSlotsMensagem.style.display = 'block';
        } else {
            if (areaAdicionarTarefas) areaAdicionarTarefas.style.display = 'block';
            if (limiteSlotsMensagem) limiteSlotsMensagem.style.display = 'none';
        }
    }
    
    function adicionarNovaTarefaNaLista(data) {
        // (Esta função não é mais usada pelo 'botaoAceitar', 
        // mas o 'handleAcaoTarefaClick' ainda pode precisar dela no futuro)
        itemListaVazia = document.getElementById('lista-tarefas-vazia');
        if (itemListaVazia) {
            itemListaVazia.remove();
            itemListaVazia = null; 
        }
        const novoLi = document.createElement('li');
        novoLi.className = 'item-tarefa';
        novoLi.id = `tarefa-${data.tarefa_id}`;
        novoLi.innerHTML = `
            <div class="tarefa-info">
                <span class="tarefa-titulo"> ${data.titulo} </span>
                <div class="tarefa-detalhes">
                    <div class="info-bloco xp-bloco">
                        <span class="info-label">XP</span>
                        <span class="info-valor">${data.xp_adicionado}</span>
                    </div>
                    ${data.descricao_completa ? `<p class="task-description-full" data-fulltext="${data.descricao_completa.replace(/"/g, '&quot;')}"></p>` : ''}
                </div>
            </div>
            <form method="POST" action="${data.url_concluir}" class="formulario-concluir">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                <button type="submit" class="botao-tarefa botao-concluir">
                    Concluir
                </button>
            </form>
        `;
        listaTarefasUL.prepend(novoLi);
        applyReadMore(novoLi);
    }

    function removerItemDaLista(tarefaLi, mensagemLog) {
        // (Seu código ... sem mudanças)
        console.log(mensagemLog);
        tarefaLi.style.opacity = '0';
        tarefaLi.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease';
        tarefaLi.style.transform = 'translateX(50px)';
        setTimeout(() => {
            tarefaLi.remove();
            if (listaTarefasUL.querySelectorAll('li.item-tarefa').length === 0) {
                listaTarefasUL.innerHTML = `
                    <li class="item-tarefa-vazia" id="lista-tarefas-vazia">
                        <p>Você não tem tarefas para hoje.</p>
                        <p>Crie tarefas recorrentes ou aguarde suas Quests Diárias!</p>
                    </li>
                `;
            }
        }, 500); 
    }

    // --- Habilita/Desabilita botão Gerar ---
    if (seletorFocoIA) {
        seletorFocoIA.addEventListener('change', function() {
            // (Seu código ... sem mudanças)
            botaoGerarIA.disabled = !this.value;
            mostrarAreaSugestao(false); feedbackIA.textContent = ''; feedbackIA.className = ''; sugestaoAtual = null;
        });
    }

    // --- Mostrar/Esconder Área Sugestão ---
    function mostrarAreaSugestao(mostrar = true) {
        // (Seu código ... sem mudanças)
        if (!areaSugestao || !botaoAceitar || !botaoDispensar) return;
        areaSugestao.style.display = mostrar ? 'block' : 'none';
        const mostrarBotaoAceitar = mostrar && sugestaoAtual;
        botaoAceitar.style.display = mostrarBotaoAceitar ? 'block' : 'none';
        botaoDispensar.style.display = mostrar ? 'block' : 'none';
    }

    // --- Gerar Sugestão (AJAX) ---
    if (botaoGerarIA) {
        botaoGerarIA.addEventListener('click', async function() {
            // (Seu código ... sem mudanças)
            const focoSelecionado = seletorFocoIA.value; if (!focoSelecionado) return;
            botaoGerarIA.disabled = true; botaoGerarIA.textContent = 'Gerando...';
            areaSugestao.innerHTML = '<p>Consultando a IA...</p>'; areaSugestao.classList.add('loading');
            feedbackIA.textContent = ''; feedbackIA.className = ''; sugestaoAtual = null;
            mostrarAreaSugestao(true);
            try {
                const response = await fetch(ajaxUrlGerar, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }, body: JSON.stringify({ foco_nome: focoSelecionado, action: 'gerar_sugestao' }) });
                areaSugestao.classList.remove('loading');
                if (!response.ok) { let msg = `E${response.status}`; try { const err = await response.json(); msg = err.error||msg;} catch(e){} throw new Error(msg); }
                const data = await response.json();
                if (!data.titulo || !data.descricao || data.xp === undefined) { throw new Error("Resposta IA incompleta."); }
                sugestaoAtual = data;
                areaSugestao.innerHTML = `
                    <p><strong>${data.titulo}</strong> <span class="xp-sugestao">(${data.xp} XP)</span></p>
                    <p class="task-description-full" data-fulltext="${data.descricao.replace(/"/g, '&quot;')}"></p>
                `;
                applyReadMore(areaSugestao); 
                feedbackIA.textContent = 'Sugestão pronta!'; feedbackIA.classList.add('sucesso');
                mostrarAreaSugestao(true);
            } catch (error) {
                console.error("Erro Gerar:", error); areaSugestao.innerHTML = '<p style="color:var(--cor-erro);">Falha.</p>'; feedbackIA.textContent = `Erro: ${error.message}. Tente.`; feedbackIA.classList.add('erro');
                sugestaoAtual = null; mostrarAreaSugestao(true);
            } finally {
                botaoGerarIA.disabled = !seletorFocoIA.value; botaoGerarIA.textContent = 'Sugerir Tarefa';
            }
        });
    }

    // --- Aceitar Sugestão (AJAX - COM Reload) ---
    if (botaoAceitar) {
        botaoAceitar.addEventListener('click', async function() {
            if (!sugestaoAtual) { console.warn("Aceitar sem sugestão."); return; }
            
            // Trava os botões
            botaoAceitar.disabled = true; 
            botaoAceitar.textContent = 'Adicionando...'; // <-- O BUG ESTAVA AQUI
            botaoDispensar.disabled = true;
            feedbackIA.textContent = 'Salvando...'; 
            feedbackIA.className = '';
            
            const sugestaoParaSalvar = { ...sugestaoAtual };

            try {
                const response = await fetch(ajaxUrlSalvar, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
                    body: JSON.stringify({
                        titulo: sugestaoParaSalvar.titulo,
                        descricao: sugestaoParaSalvar.descricao,
                        xp: sugestaoParaSalvar.xp,
                        action: 'salvar_sugestao'
                    })
                });
                
                if (!response.ok) { 
                    let msg = `Erro ${response.status}`; 
                    try { const err = await response.json(); msg = err.error || msg; } catch(e){} 
                    throw new Error(msg); // Lança o erro (ex: "Limite atingido")
                }
                
                const data = await response.json();
                if (!data.success || !data.tarefa_id) { throw new Error(data.error || "Resposta inválida."); }

                // --- MUDANÇA (O "REFRESHZINHO" QUE VOCÊ PEDIU) ---
                feedbackIA.textContent = `Tarefa adicionada! (+${data.xp_adicionado} XP) Atualizando...`;
                feedbackIA.classList.add('sucesso');
                sugestaoAtual = null; 
                
                // Espera um pouquinho para o usuário ler o feedback
                // e depois recarrega a página.
                setTimeout(() => {
                    location.reload(); 
                }, 750); // 750ms de espera
                // ---------------------------------------------

            } catch (error) {
                console.error("Erro Salvar:", error); 
                feedbackIA.textContent = `Erro: ${error.message}`; // Mostra o erro (ex: limite atingido)
                feedbackIA.classList.add('erro');
                sugestaoAtual = sugestaoParaSalvar; 
                
                // --- MUDANÇA: Reabilita os botões se FALHAR ---
                // (Isso também conserta o bug)
                botaoAceitar.disabled = false; 
                botaoAceitar.textContent = 'Adicionar esta Tarefa';
                botaoDispensar.disabled = false;
                // ------------------------------------------
                
                mostrarAreaSugestao(true);
            }
        });
    }

    // --- Dispensar Sugestão ---
    if (botaoDispensar) {
        botaoDispensar.addEventListener('click', function() {
            // (Seu código ... sem mudanças)
            console.log("Dispensar clicado.");
            sugestaoAtual = null; mostrarAreaSugestao(false); areaSugestao.innerHTML = ''; feedbackIA.textContent = ''; feedbackIA.className = '';
            if (botaoGerarIA) botaoGerarIA.disabled = !seletorFocoIA.value;
        });
    }


    // --- LÓGICA AJAX PARA CONCLUIR / DESCARTAR ---
    async function handleAcaoTarefaClick(event) {
        // (Seu código ... sem mudanças)
        const botaoClicado = event.target.closest('button.botao-tarefa');
        if (!botaoClicado) { return; }
        event.preventDefault(); 
        const form = botaoClicado.closest('form');
        const url = form.action; 
        const tarefaLi = form.closest('li.item-tarefa');
        const tarefaId = tarefaLi ? tarefaLi.id.split('-')[1] : null;
        if (!url || !tarefaLi || !tarefaId) { 
            console.error("Erro na Ação: URL/ID da tarefa não encontrado."); 
            return; 
        }
        if (botaoClicado.classList.contains('botao-desmarcar')) {
            form.submit();
            return;
        }
        console.log(`Ação AJAX para Tarefa ID: ${tarefaId} (URL: ${url})`);
        botaoClicado.disabled = true; 
        botaoClicado.textContent = '...';
        tarefaLi.querySelectorAll('.botao-tarefa').forEach(b => b.disabled = true);
        try {
            const response = await fetch(url, { 
                method: 'POST', 
                headers: { 
                    'X-CSRFToken': csrftoken, 
                    'X-Requested-With': 'XMLHttpRequest' 
                } 
            });
            if (!response.ok) { 
                let msg = `E${response.status}`; 
                try{ const err=await response.json(); msg=err.error||msg; } catch(e){} 
                throw new Error(msg); 
            }
            const data = await response.json();
            if (data.success) {
                if (data.concluida) {
                    removerItemDaLista(tarefaLi, `Tarefa ${tarefaId} concluída. Ganhou ${data.xp_ganho} XP.`);
                    if (typeof atualizarBarraDeXP === 'function') {
                        atualizarBarraDeXP(data); 
                    } else {
                        console.warn("Função 'atualizarBarraDeXP' não encontrada.");
                    }
                }
                else if (data.descartada) {
                     removerItemDaLista(tarefaLi, `Tarefa ${tarefaId} descartada.`);
                }
                else if (!data.concluida) { 
                    console.log(`Tarefa ${tarefaId} desmarcada. Perdeu ${data.xp_ganho} XP.`);
                    location.reload(); 
                }
            } else { 
                throw new Error(data.error || "Erro retornado."); 
            }
        } catch (error) {
            console.error("Erro AJAX na Ação:", error);
            tarefaLi.querySelectorAll('.botao-tarefa').forEach(b => b.disabled = false);
            if (botaoClicado.classList.contains('botao-concluir')) botaoClicado.textContent = 'Concluir';
            if (botaoClicado.classList.contains('botao-concluir-atrasada')) botaoClicado.textContent = 'Concluir (sem XP)';
            if (botaoClicado.classList.contains('botao-descartar')) botaoClicado.textContent = 'Descartar';
            alert(`Erro: ${error.message}`);
        }
    }
    
    if (listaTarefasUL) {
        listaTarefasUL.addEventListener('click', handleAcaoTarefaClick);
    }
    // === FIM LÓGICA CONCLUIR/DESCARTAR ===

    // --- Inicialização ---
    console.log("Inicializando...");
    if (areaSugestao) {
        mostrarAreaSugestao(false);
    }
    applyReadMore(listaTarefasUL);
    atualizarContadorSlots();
    console.log("Inicialização completa.");

});