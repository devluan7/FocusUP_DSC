// static/home/js/lista_tarefas_ai.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("lista_tarefas_ai.js Carregado! v10 (Fix 'Ler Mais')");

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
    const ajaxUrlGerar = container ? container.dataset.ajaxUrlGerar : null;
    const ajaxUrlSalvar = container ? container.dataset.ajaxUrlSalvar : null;
    const csrftoken = container ? container.dataset.csrfToken : null;

    let sugestaoAtual = null; // Guarda a sugestão {titulo, descricao, dificuldade, xp}

    // --- Verificações Iniciais ---
    if (!seletorFocoIA || !botaoGerarIA || !areaSugestao || !feedbackIA || !botaoAceitar || !botaoDispensar || !listaTarefasUL || !ajaxUrlGerar || !ajaxUrlSalvar || !csrftoken) {
        console.error("ERRO: Elementos essenciais da IA não encontrados.");
        if (botaoGerarIA) botaoGerarIA.disabled = true; if (seletorFocoIA) seletorFocoIA.disabled = true;
        return;
    }
    console.log("Elementos da IA encontrados.");

    // --- FUNÇÃO "LER MAIS" (CORRIGIDA) ---
    const MAX_CHARS_DESCRIPTION = 100; // Limite de caracteres

    function applyReadMore(parentElement) {
        if (!parentElement) {
            console.warn("applyReadMore chamado sem parentElement.");
            return;
        }
        
        // Pega todas as descrições (na lista E na área de sugestão)
        const descriptions = parentElement.querySelectorAll('.task-description-full[data-fulltext]');
        console.log(`[Ler Mais] Encontradas ${descriptions.length} descrições.`);

        descriptions.forEach((desc) => {
            const fullText = desc.dataset.fulltext;
            
            // Limpa o conteúdo atual (pode ter texto do template Django)
            desc.innerHTML = ''; 

            if (fullText.length > MAX_CHARS_DESCRIPTION) {
                // Texto é longo, precisa truncar
                const shortText = fullText.substring(0, MAX_CHARS_DESCRIPTION) + "...";
                
                // 1. Cria o SPAN para o texto
                const textSpan = document.createElement('span');
                textSpan.className = 'description-text'; // Classe para fácil seleção
                textSpan.textContent = shortText;
                
                // 2. Cria o BOTÃO "Ler Mais"
                const readMoreLink = document.createElement('button');
                readMoreLink.textContent = " Ler Mais";
                readMoreLink.className = 'read-more-link';
                readMoreLink.type = 'button'; // Evita submit de form

                // 3. Adiciona ambos ao parágrafo
                desc.appendChild(textSpan);
                desc.appendChild(readMoreLink);
                desc.classList.add('truncated'); // Adiciona classe para controle (ex: CSS fade)

                // 4. Adiciona a lógica de clique CORRETA
                readMoreLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log("[Ler Mais] Clique detectado!");
                    
                    if (desc.classList.contains('truncated')) {
                        // Expandir
                        textSpan.textContent = fullText; // Altera SÓ o texto
                        readMoreLink.textContent = " Ler Menos"; // Altera SÓ o botão
                        desc.classList.remove('truncated');
                        console.log("[Ler Mais] Expandido.");
                    } else {
                        // Recolher
                        textSpan.textContent = shortText; // Altera SÓ o texto
                        readMoreLink.textContent = " Ler Mais"; // Altera SÓ o botão
                        desc.classList.add('truncated');
                        console.log("[Ler Mais] Recolhido.");
                    }
                });
            } else {
                // Texto é curto, apenas exibe
                desc.textContent = fullText;
                desc.classList.remove('truncated');
            }
        });
    }
    // ======================================


    // --- Habilita/Desabilita botão Gerar ---
    seletorFocoIA.addEventListener('change', function() {
        botaoGerarIA.disabled = !this.value;
        mostrarAreaSugestao(false); feedbackIA.textContent = ''; feedbackIA.className = ''; sugestaoAtual = null;
    });

    // --- Mostrar/Esconder Área Sugestão ---
    function mostrarAreaSugestao(mostrar = true) {
        if (!areaSugestao || !botaoAceitar || !botaoDispensar) return;
        areaSugestao.style.display = mostrar ? 'block' : 'none';
        const mostrarBotaoAceitar = mostrar && sugestaoAtual;
        botaoAceitar.style.display = mostrarBotaoAceitar ? 'block' : 'none';
        botaoDispensar.style.display = mostrar ? 'block' : 'none';
    }

    // --- Gerar Sugestão (AJAX) ---
    botaoGerarIA.addEventListener('click', async function() {
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
            
            // Cria o HTML base da sugestão
            areaSugestao.innerHTML = `
                <p><strong>${data.titulo}</strong> <span class="xp-sugestao">(${data.xp} XP)</span></p>
                <p class="task-description-full" data-fulltext="${data.descricao.replace(/"/g, '&quot;')}">${data.descricao}</p>
            `;
            // CHAMA A FUNÇÃO CORRIGIDA para a sugestão recém-criada
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

    // --- Aceitar Sugestão (AJAX - Com Reload) ---
    botaoAceitar.addEventListener('click', async function() {
        if (!sugestaoAtual) { console.warn("Aceitar sem sugestão."); return; }
        botaoAceitar.disabled = true; botaoAceitar.textContent = 'Adicionando...';
        botaoDispensar.disabled = true;
        feedbackIA.textContent = 'Salvando...'; feedbackIA.className = '';
        const sugestaoParaSalvar = { ...sugestaoAtual };

        try {
            const response = await fetch(ajaxUrlSalvar, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({
                    titulo: sugestaoParaSalvar.titulo,
                    descricao: sugestaoParaSalvar.descricao,
                    xp: sugestaoParaSalvar.xp, // Envia o XP
                    action: 'salvar_sugestao'
                })
            });
            if (!response.ok) { let msg = `E${response.status}`; try { const err = await response.json(); msg = err.error||msg; } catch(e){} throw new Error(msg); }
            const data = await response.json();
            if (!data.success || !data.tarefa_id) { throw new Error(data.error || "Resposta inválida."); }

            // SUCESSO AO SALVAR -> RECARREGA A PÁGINA
            feedbackIA.textContent = `Tarefa adicionada! (+${data.xp_adicionado} XP) Recarregando...`;
            feedbackIA.classList.add('sucesso');
            sugestaoAtual = null; 
            setTimeout(() => { location.reload(); }, 750); // Recarrega

        } catch (error) {
            console.error("Erro Salvar:", error); feedbackIA.textContent = `Erro salvar: ${error.message}`; feedbackIA.classList.add('erro');
            sugestaoAtual = sugestaoParaSalvar; // Restaura sugestão
            botaoAceitar.disabled = false; // Reabilita botões
            botaoDispensar.disabled = false;
            mostrarAreaSugestao(true);
        }
    });

    // --- Dispensar Sugestão ---
    botaoDispensar.addEventListener('click', function() {
        console.log("Dispensar clicado.");
        sugestaoAtual = null; mostrarAreaSugestao(false); areaSugestao.innerHTML = ''; feedbackIA.textContent = ''; feedbackIA.className = '';
        botaoGerarIA.disabled = !seletorFocoIA.value;
    });

    // --- LÓGICA AJAX PARA CONCLUIR ---
     async function handleConcluirClick(event) {
        if (!event.target.matches('.formulario-concluir button.botao-tarefa')) { return; }
        event.preventDefault();
        const botaoClicado = event.target;
        const form = botaoClicado.closest('form');
        const url = form.action;
        const tarefaLi = form.closest('li.item-tarefa');
        const tarefaId = tarefaLi ? tarefaLi.id.split('-')[1] : null;
        if (!url || !tarefaLi || !tarefaId) { console.error("Erro concluir: URL/ID."); return; }
        // Se for desmarcar, faz o POST normal (recarrega a página)
        if (botaoClicado.classList.contains('botao-desmarcar')) {
             console.log("Desmarcando Tarefa ID:", tarefaId, "(via POST normal)");
             form.submit();
             return;
        } 
        
        console.log(`Concluir Tarefa ID: ${tarefaId} (via AJAX)`);
        botaoClicado.disabled = true; botaoClicado.textContent = '...';

        try {
            const response = await fetch(url, { method: 'POST', headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' } });
            if (!response.ok) { let msg = `E${response.status}`; try{const err=await response.json();msg=err.error||msg;}catch(e){} throw new Error(msg); }
            const data = await response.json();
            
            if (data.success && data.concluida) { // Marcada como concluída
                console.log(`Tarefa ${tarefaId} concluída. Ganhou ${data.xp_ganho} XP. Removendo.`);
                tarefaLi.style.opacity = '0';
                tarefaLi.style.transition = 'opacity 0.5s ease-out';
                setTimeout(() => {
                    tarefaLi.remove(); // Remove o item
                    location.reload(); // Recarrega para atualizar XP Total
                }, 500); // 500ms para a animação
            } else if (data.success && !data.concluida) { // Desmarcada
                 console.log(`Tarefa ${tarefaId} desmarcada. Perdeu ${data.xp_ganho} XP.`);
                 location.reload(); // Recarrega para atualizar XP
            } else { throw new Error(data.error || "Erro retornado."); }
        } catch (error) {
            console.error("Erro AJAX concluir:", error);
            botaoClicado.disabled = false; botaoClicado.textContent = 'Concluir';
            alert(`Erro: ${error.message}`);
        }
    }
    if (listaTarefasUL) {
        listaTarefasUL.addEventListener('click', handleConcluirClick);
    }
    // === FIM LÓGICA CONCLUIR ===

    // --- Inicialização ---
    console.log("Inicializando...");
    mostrarAreaSugestao(false);
    // Aplica "Ler Mais" aos itens que já estão na lista ao carregar
    applyReadMore(listaTarefasUL); 
    console.log("Inicialização completa.");

});