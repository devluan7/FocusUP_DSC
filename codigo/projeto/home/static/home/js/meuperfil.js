// Espera o HTML carregar completamente antes de rodar o script
document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. Seleciona os Elementos do Formulário ---
    
    // Campo principal de seleção do Foco
    const selectFoco = document.getElementById('id_foco_nome_select'); 
    
    // Campo genérico de Observações Adicionais
    const textareaDetalhes = document.getElementById('id_detalhes_textarea'); 
    
    // Div que contém os campos específicos da Academia (começa escondida)
    const divCamposAcademia = document.getElementById('campos-academia');
    
    // Adicione aqui seletores para divs de outros focos (ex: campos-estudos) se criar
    // const divCamposEstudos = document.getElementById('campos-estudos');
    
    // Campos específicos DENTRO da div de Academia
    const inputPeso = document.getElementById('id_extra_peso');
    const selectNivel = document.getElementById('id_extra_nivel_treino');
    const selectLocal = document.getElementById('id_extra_local_treino');
    const selectFreq = document.getElementById('id_extra_freq_treino');
    const inputObjetivoAcademia = document.getElementById('id_extra_objetivo_academia');
    
    // Adicione aqui seletores para campos de outros focos
    
    // --- 2. Pega os Dados dos Perfis Salvos (do Django) ---
    
    const perfisDataElement = document.getElementById('perfis-data');
    let perfisData = {}; 
    if (perfisDataElement) {
        try {
            perfisData = JSON.parse(perfisDataElement.textContent);
        } catch (e) {
            console.error("Erro ao ler os dados dos perfis (JSON inválido?):", e);
        }
    } else {
        console.warn("Elemento 'perfis-data' não encontrado. Preenchimento não funcionará.");
    }

    // --- 3. Placeholders Dinâmicos ---
    // Define as dicas para cada foco (adicione mais conforme necessário)
    const placeholdersDetalhes = {
        'academia': 'Ex: Quero focar em hipertrofia de pernas, tenho lesão no ombro...',
        'estudos': 'Ex: Sou estudante de Direito (5º sem), preciso melhorar em Direito Penal, meu objetivo é passar na OAB...',
        'trabalho': 'Ex: Trabalho como Designer (remoto), quero melhorar minha gestão de tempo e comunicação com a equipe...',
        'saude': 'Ex: Quero reduzir a ansiedade, dormir melhor, talvez experimentar meditação...',
        'casa': 'Ex: Preciso criar uma rotina para limpar o banheiro 1x/semana e não deixar a louça acumular...',
        'lazer': 'Ex: Quero voltar a tocar violão pelo menos 2x/semana, ler mais ficção...',
        'outro': 'Descreva este foco e seus objetivos...',
        '': 'Descreva seus objetivos, dificuldades, preferências, etc. Quanto mais detalhes, melhor a IA!' // Placeholder padrão
    };

    // --- 4. Funções Principais ---

    // Função para mostrar/esconder seções de campos específicos
    function atualizarVisibilidadeCampos() {
        const focoSelecionado = selectFoco ? selectFoco.value : '';

        // Esconde todas as seções primeiro
        if (divCamposAcademia) divCamposAcademia.style.display = 'none';
        // Adicione aqui linhas para esconder outras divs (ex: divCamposEstudos.style.display = 'none';)

        // Mostra a seção correspondente ao foco
        if (focoSelecionado === 'academia' && divCamposAcademia) {
            divCamposAcademia.style.display = 'block';
        }
        // Adicione aqui 'else if' para mostrar outras divs (ex: else if (focoSelecionado === 'estudos' && divCamposEstudos) ...)
    }

    // Função para preencher (ou limpar) os campos do formulário
    function preencherFormulario() {
        if (!selectFoco) return; // Se o select não existe, não faz nada

        const focoSelecionado = selectFoco.value; 
        const dadosPerfil = perfisData[focoSelecionado]; // Pega os dados salvos para este foco

        // --- Preenche/Limpa Campos Específicos (Academia) ---
        if (inputPeso) inputPeso.value = dadosPerfil?.dados_especificos?.peso || '';
        if (selectNivel) selectNivel.value = dadosPerfil?.dados_especificos?.nivel_treino || '';
        if (selectLocal) selectLocal.value = dadosPerfil?.dados_especificos?.local_treino || '';
        if (selectFreq) selectFreq.value = dadosPerfil?.dados_especificos?.freq_treino || '';
        if (inputObjetivoAcademia) inputObjetivoAcademia.value = dadosPerfil?.dados_especificos?.objetivo_academia || '';
        
        // Adicione aqui linhas para preencher/limpar campos de outros focos

        // --- Preenche/Limpa Campo de Observações Detalhadas ---
        if (textareaDetalhes) {
            textareaDetalhes.value = dadosPerfil?.detalhes || ''; 
            // Atualiza o placeholder com a dica relevante
            textareaDetalhes.placeholder = placeholdersDetalhes[focoSelecionado] || placeholdersDetalhes[''];
        }
    }

    // --- 5. Lógica Inicial e Event Listeners ---

    // Garante que o selectFoco existe
    if (selectFoco) {
        // Define o estado inicial da visibilidade e preenchimento ao carregar a página
        atualizarVisibilidadeCampos();
        preencherFormulario(); 

        // Adiciona o "ouvinte" para quando o usuário MUDAR a seleção do foco
        selectFoco.addEventListener('change', function() {
            atualizarVisibilidadeCampos(); // Mostra/esconde os campos certos
            preencherFormulario();       // Preenche/limpa os campos
        });
    } else {
        console.error("Elemento 'id_foco_nome_select' (select principal) não encontrado.");
    }

}); // Fim do 'DOMContentLoaded'