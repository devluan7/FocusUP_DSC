document.addEventListener('DOMContentLoaded', function() {
    const seletorFocoIA = document.getElementById('seletor-foco-ia');
    const botaoGerarIA = document.getElementById('botao-gerar-ia');
    const areaSugestaoIA = document.getElementById('area-sugestao-ia');
    const feedbackIA = document.getElementById('feedback-ia');
    const botaoAceitar = document.getElementById('botao-aceitar-sugestao');

    const formTarefa = document.getElementById('form-tarefa');
    const inputTitulo = document.getElementById('id_titulo');
    const textareaDescricao = document.getElementById('id_descricao');

    const formContainer = document.querySelector('.form-container');
    const ajaxUrl = formContainer ? formContainer.dataset.ajaxUrl : null;
    const csrftoken = formContainer ? formContainer.dataset.csrfToken : null;

    let sugestaoAtual = null;

    // === NOVO: SUGESTÕES PRÉ-DEFINIDAS PARA FALLBACK ===
    // (Melhore estas sugestões para serem mais criativas e variadas!)
    const predefinedSuggestions = {
        'academia': [
            { titulo: "Ritmo Constante", descricao: "Que tal manter a consistência hoje? Dedique o tempo planejado ao seu treino na academia, focando na execução correta dos exercícios para seu objetivo." },
            { titulo: "Energia Matinal", descricao: "Comece o dia com foco! Se treina de manhã, prepare seu equipamento na noite anterior para facilitar a rotina." },
            { titulo: "Hidratação é Chave", descricao: "Lembre-se de beber água suficiente durante o treino de hoje. Manter-se hidratado otimiza seus resultados na academia." }
        ],
        'estudos': [
            { titulo: "Sessão Focada", descricao: "Reserve um bloco de tempo (ex: 45 min) hoje sem distrações para revisar aquela matéria mais desafiadora. O progresso contínuo é fundamental!" },
            { titulo: "Mapa Mental", descricao: "Experimente criar um mapa mental sobre o tópico que está estudando. Visualizar as conexões pode clarear suas ideias." },
            { titulo: "Pequena Revisão", descricao: "Que tal dedicar 15 minutos antes de dormir para revisar brevemente o que estudou hoje? Ajuda a fixar o conhecimento." }
        ],
        'trabalho': [
            { titulo: "Prioridade do Dia", descricao: "Identifique a tarefa MAIS importante de hoje e comece por ela. Concluí-la trará uma grande sensação de avanço no seu trabalho." },
            { titulo: "Organizar a Semana", descricao: "Dedique 10 minutos para planejar suas principais tarefas para os próximos dias. Uma boa organização evita a sobrecarga no trabalho." },
            { titulo: "Limpeza Digital", descricao: "Organize sua caixa de entrada ou a pasta de downloads. Um ambiente digital limpo melhora o foco no trabalho." }
        ],
        'saude': [
            { titulo: "Pausa Consciente", descricao: "Faça uma pequena pausa ativa hoje (ex: 5 min de alongamento) a cada hora de trabalho/estudo. Cuidar da postura e circulação é essencial para a saúde." },
            { titulo: "Lanche Saudável", descricao: "Planeje e prepare um lanche nutritivo para hoje (fruta, iogurte, nuts). Pequenas escolhas alimentares impactam sua saúde geral." },
            { titulo: "Respiração Profunda", descricao: "Reserve 3 minutos para praticar respirações profundas e conscientes. Ajuda a reduzir o estresse e melhora o foco e a saúde mental." }
        ],
        'casa': [
            { titulo: "Missão 10 Minutos", descricao: "Escolha um cômodo e dedique apenas 10 minutos para uma organização rápida (arrumar cama, guardar objetos). Manter a casa em ordem contribui para o bem-estar." },
            { titulo: "Cozinha em Ordem", descricao: "Que tal lavar a louça logo após a refeição hoje? Evitar o acúmulo deixa a cozinha mais agradável e funcional." },
            { titulo: "Planejar Refeição", descricao: "Pense no que vai cozinhar amanhã e já separe os ingredientes ou adiante algum preparo. Planejar facilita a rotina em casa." }
        ],
        'lazer': [
            { titulo: "Momento Relax", descricao: "Reserve um tempo definido hoje (mesmo que curto) para seu hobby preferido. Desconectar é importante para recarregar as energias." },
            { titulo: "Explorar Algo Novo", descricao: "Que tal ouvir uma música diferente, ler sobre um assunto novo ou assistir a um documentário curto? Expande seus horizontes no lazer." },
            { titulo: "Contato Social", descricao: "Mande uma mensagem ou ligue para um amigo ou familiar hoje. Conexões sociais são parte importante do lazer e bem-estar." }
        ],
        // Fallback genérico caso o foco não esteja mapeado
        'default': [
            { titulo: "Pequeno Passo", descricao: "Escolha uma pequena tarefa que você está adiando e dedique 15 minutos a ela hoje. Começar é o mais importante!" },
            { titulo: "Organizar o Amanhã", descricao: "Antes de dormir, anote as 3 principais coisas que você quer realizar amanhã. Ajuda a começar o dia com clareza."}
        ]
    };
    // ======================================================

    // (Verificações iniciais - mantenha como antes)
    if (!seletorFocoIA || !botaoGerarIA || !areaSugestaoIA || !feedbackIA || !botaoAceitar || !formTarefa || !inputTitulo || !textareaDescricao || !ajaxUrl || !csrftoken) {
        console.error("ERRO: Elementos essenciais ou data attributes não encontrados. IA desativada.");
        // (Desabilitar botões, etc.)
        return;
    }

    // Habilita/Desabilita botão Gerar
    seletorFocoIA.addEventListener('change', function() {
        botaoGerarIA.disabled = !this.value;
    });

    // --- Gerar Sugestão ---
    botaoGerarIA.addEventListener('click', async function() {
        const focoSelecionado = seletorFocoIA.value; // Ex: 'academia'
        if (!focoSelecionado) return;

        // Reset visual e de estado
        botaoGerarIA.disabled = true;
        botaoGerarIA.textContent = 'Gerando...';
        areaSugestaoIA.innerHTML = '<p>Aguarde, consultando a IA...</p>';
        areaSugestaoIA.classList.add('loading');
        feedbackIA.textContent = '';
        feedbackIA.className = '';
        botaoAceitar.style.display = 'none';
        sugestaoAtual = null;

        try {
            // Tenta chamar a IA real
            console.log("Tentando chamar IA real...");
            const response = await fetch(ajaxUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ foco_nome: focoSelecionado, action: 'gerar_sugestao' })
            });

            areaSugestaoIA.classList.remove('loading');

            if (!response.ok) {
                let errorMessage = `Erro ${response.status}`;
                try { const errorData = await response.json(); errorMessage = errorData.error || errorMessage; } catch(e) {}
                // NÃO lança o erro ainda, vamos tentar o fallback
                console.warn("Falha na IA real:", errorMessage);
                throw new Error("Falha na IA real"); // Força a ida para o catch
            }

            const data = await response.json();
            if (!data.titulo || !data.descricao) {
                 console.warn("Resposta da IA incompleta:", data);
                 throw new Error("Resposta da IA incompleta"); // Força a ida para o catch
            }

            // SUCESSO DA IA REAL!
            console.log("IA Real retornou sucesso:", data);
            sugestaoAtual = data;
            areaSugestaoIA.innerHTML = `
                <p><strong>Título Sugerido:</strong> ${data.titulo}</p>
                <p><strong>Descrição Sugerida:</strong> ${data.descricao.replace(/\n/g, '<br>')}</p>
            `;
            botaoAceitar.style.display = 'inline-block';
            feedbackIA.textContent = 'Sugestão da IA pronta!'; // Mensagem um pouco diferente
            feedbackIA.classList.add('sucesso');

        // === BLOCO CATCH ATUALIZADO COM FALLBACK ===
        } catch (error) {
            console.error("Erro ao gerar sugestão (real ou fallback):", error);

            // TENTA USAR SUGESTÃO PRÉ-DEFINIDA
            console.log("Tentando fallback com sugestão pré-definida para:", focoSelecionado);
            const sugestoesParaFoco = predefinedSuggestions[focoSelecionado.toLowerCase()] || predefinedSuggestions['default'];
            if (sugestoesParaFoco && sugestoesParaFoco.length > 0) {
                // Seleciona uma sugestão aleatória da lista
                const randomIndex = Math.floor(Math.random() * sugestoesParaFoco.length);
                const fallbackSuggestion = sugestoesParaFoco[randomIndex];
                console.log("Fallback selecionado:", fallbackSuggestion);

                sugestaoAtual = fallbackSuggestion; // Guarda a sugestão de fallback

                areaSugestaoIA.classList.remove('loading'); // Garante remover loading
                areaSugestaoIA.innerHTML = `
                    <p><strong>Título Sugerido:</strong> ${fallbackSuggestion.titulo}</p>
                    <p><strong>Descrição Sugerida:</strong> ${fallbackSuggestion.descricao.replace(/\n/g, '<br>')}</p>
                `;
                botaoAceitar.style.display = 'inline-block'; // Mostra o botão de aceitar
                feedbackIA.textContent = 'Sugestão Pronta!'; // Mensagem de sucesso genérica (esconde a falha da IA)
                feedbackIA.className = 'sucesso';

            } else {
                // Se nem o fallback funcionar (improvável)
                console.error("Falha ao encontrar sugestão de fallback para:", focoSelecionado);
                areaSugestaoIA.innerHTML = '<p style="color: var(--cor-erro);">Oops! Falha ao gerar sugestão.</p>';
                feedbackIA.textContent = `Erro interno ao buscar sugestão. Tente novamente mais tarde.`;
                feedbackIA.className = 'erro';
                sugestaoAtual = null;
                botaoAceitar.style.display = 'none';
            }
            // --- FIM DA LÓGICA DE FALLBACK ---

        } finally {
            // Reabilita o botão Gerar, independentemente do resultado
            botaoGerarIA.disabled = !seletorFocoIA.value;
            botaoGerarIA.textContent = 'Gerar Sugestão';
        }
    });

    // --- Aceitar Sugestão ---
    botaoAceitar.addEventListener('click', function() {
        if (sugestaoAtual && inputTitulo && textareaDescricao) {
            inputTitulo.value = sugestaoAtual.titulo;
            textareaDescricao.value = sugestaoAtual.descricao;
            // Opcional: formTarefa.scrollIntoView({ behavior: 'smooth', block: 'start' });
            feedbackIA.textContent = 'Formulário preenchido! Ajuste se necessário e salve.';
            feedbackIA.className = 'sucesso';
            // Opcional: Esconder botão após clique
            // botaoAceitar.style.display = 'none';
        } else {
           console.error("Não foi possível preencher. Sugestão:", sugestaoAtual, "Titulo Input:", inputTitulo, "Desc Textarea:", textareaDescricao);
           feedbackIA.textContent = 'Erro ao tentar preencher o formulário.';
           feedbackIA.className = 'erro';
        }
    });

});