document.addEventListener('DOMContentLoaded', function () {
  console.log("meuperfil.js CARREGADO!");

  // --- Elementos Globais ---
  const perfisDataElement = document.getElementById('perfis-data');
  if (!perfisDataElement) { console.error('ERRO: Elemento #perfis-data não encontrado.'); return; }
  const perfisDados = JSON.parse(perfisDataElement.textContent);
  console.log("Dados dos perfis:", perfisDados);

  const seletorPerfil = document.getElementById('seletor-perfil'); 		// Dropdown de cima (visualização)
  const containerDinamico = document.getElementById('container-dinamico-perfil');
  const areaExibicao = document.getElementById('exibicao-perfil'); 		// Div de visualização
  const secaoFormulario = document.getElementById('secao-formulario'); 	// Div do formulário
  const form = document.getElementById('perfil-foco-form');
  const formFocoSelect = form ? form.querySelector('#id_foco_nome_select') : null; // Select DENTRO do form
  const formDetalhes = document.getElementById('id_detalhes_textarea'); // Confirme ID!
  const botaoCancelar = document.getElementById('botao-cancelar-js');

  // --- Divs de campos específicos ---
  const camposAcademia = document.getElementById('campos-academia');
  const camposEstudos = document.getElementById('campos-estudos');
  const camposTrabalho = document.getElementById('campos-trabalho');
  const camposSaude = document.getElementById('campos-saude');
  const camposCasa = document.getElementById('campos-casa');
  const camposLazer = document.getElementById('campos-lazer');
  const todasAsDivsCampos = [ camposAcademia, camposEstudos, camposTrabalho, camposSaude, camposCasa, camposLazer ];

  // --- Campos específicos (IDs definidos no forms.py) ---
  // Academia
  const formAltura = document.getElementById('id_extra_altura');
  const formPeso = document.getElementById('id_extra_peso');
  const formNivelTreino = document.getElementById('id_extra_nivel_treino');
  const formLocalTreino = document.getElementById('id_extra_local_treino');
  const formFreqTreino = document.getElementById('id_extra_freq_treino');
  const formObjetivoAcademia = document.getElementById('id_extra_objetivo_academia');
  // Estudos
  const formTipoEstudante = document.getElementById('id_extra_tipo_estudante');
  const formAreaEstudo = document.getElementById('id_extra_area_estudo');
  const formPeriodoEstudo = document.getElementById('id_extra_periodo_preferido_estudo');
  // Trabalho
  const formAreaTrabalho = document.getElementById('id_extra_area_trabalho');
  const formModalidadeTrabalho = document.getElementById('id_extra_modalidade_trabalho');
  const formCargoAtual = document.getElementById('id_extra_cargo_atual');
  // Saúde
  const formObjetivoSaude = document.getElementById('id_extra_objetivo_saude');
  const formAcompanhamento = document.getElementById('id_extra_acompanhamento_medico');
  const formRestricao = document.getElementById('id_extra_restricao_alimentar');
  // Casa
  const formTipoMoradia = document.getElementById('id_extra_tipo_moradia');
  const formTarefaCasa = document.getElementById('id_extra_tarefa_principal_casa');
  const formMoraSozinho = document.getElementById('id_extra_mora_sozinho');
  // Lazer
  const formHobby = document.getElementById('id_extra_hobby_principal');
  const formFreqLazer = document.getElementById('id_extra_freq_lazer');
  const formTipoLazer = document.getElementById('id_extra_tipo_lazer_preferido');

  const mapFocoParaDivId = {
      'academia': 'campos-academia',
      'estudos': 'campos-estudos',
      'trabalho': 'campos-trabalho',
      'saude': 'campos-saude',
      'casa': 'campos-casa',
      'lazer': 'campos-lazer',
  };

  // --- Verificações Iniciais ---
  let inicializacaoOk = true;
  if (!seletorPerfil) { console.error("ERRO: #seletor-perfil não encontrado!"); inicializacaoOk = false; }
  if (!containerDinamico) { console.error("ERRO: #container-dinamico-perfil não encontrado!"); inicializacaoOk = false; }
  if (!areaExibicao) { console.error("ERRO: #exibicao-perfil não encontrado!"); inicializacaoOk = false; }
  if (!secaoFormulario) { console.error("ERRO: #secao-formulario não encontrado!"); inicializacaoOk = false; }
  if (!form) { console.error("ERRO: #perfil-foco-form não encontrado!"); inicializacaoOk = false; }
  if (!formFocoSelect) { console.error("ERRO: #id_foco_nome_select (SELECT do formulário) não encontrado!"); inicializacaoOk = false; }
  if (!formDetalhes) { console.error("ERRO: #id_detalhes_textarea não encontrado!"); inicializacaoOk = false; }
  if (!botaoCancelar) { console.error("ERRO: #botao-cancelar-js não encontrado!"); inicializacaoOk = false; }
  // Poderíamos adicionar verificações para TODOS os campos extras aqui também
  if (!inicializacaoOk) { console.error("Inicialização falhou."); return; }

  let perfilSelecionadoAtual = null;

  const placeholdersExemplo = {
    'academia': 'Ex: Quero focar em hipertrofia, treino 5x/semana na academia do prédio...',
    'estudos': 'Ex: Preciso estudar para a prova de cálculo, 2h por dia, prefiro à noite...',
    'trabalho': 'Ex: Projeto importante para entregar até sexta, organizar tarefas diárias...',
    'saude': 'Ex: Beber 2L de água por dia, lembrar vitaminas, caminhadas 3x/semana...',
    'casa': 'Ex: Limpeza semanal (seg/qua/sex), compras no sábado, consertar torneira...',
    'lazer': 'Ex: Ler 1 capítulo por dia, filme no fds, sair com amigos sexta...',
    'outro': 'Descreva seu objetivo específico, dificuldades, preferências...',
    '': 'Descreva seus objetivos, dificuldades, preferências...'
  };

  // --- Funções Auxiliares ---

  function toggleCamposEspeciaisFormulario(nomePerfil) {
      const focoKey = nomePerfil ? nomePerfil.toLowerCase() : '';
      const idDivParaMostrar = mapFocoParaDivId[focoKey];
      // console.log(`Toggle: Foco Key = ${focoKey}, Div ID to show = ${idDivParaMostrar}`); // DEBUG

      todasAsDivsCampos.forEach(div => {
          if (div) {
              // console.log(`Checking div: ${div.id}`); // DEBUG
              if (div.id === idDivParaMostrar) {
                  // console.log(`Showing ${div.id}`); // DEBUG
                  
                  // #############################################
                  // #         ✨ A CORREÇÃO ESTÁ AQUI ✨         #
                  // #############################################
                  div.style.display = 'block'; // ANTES ESTAVA 'flex'
                  
              } else {
                  // console.log(`Hiding ${div.id}`); // DEBUG
                  div.style.display = 'none';
              }
          } // else { console.warn("Found a null div"); } // DEBUG
      });
  }

  function atualizarPlaceholderDetalhes(nomePerfil) {
      const placeholderKey = nomePerfil ? nomePerfil.toLowerCase() : '';
      const textoPlaceholder = placeholdersExemplo[placeholderKey] || placeholdersExemplo[''];
      if (formDetalhes) {
          formDetalhes.placeholder = textoPlaceholder;
      }
  }

  function atualizarExibicao(nomePerfil) {
    console.log("Atualizando exibição para:", nomePerfil); // Ex: 'academia'
    perfilSelecionadoAtual = nomePerfil;
    const perfil = perfisDados[nomePerfil]; // Busca dados salvos (case sensitive!)
    if (form) form.classList.remove('editando');

    if (!nomePerfil) {
      areaExibicao.innerHTML = `<p class="perfil-vazio-js">Selecione um perfil acima.</p>`;
      mostrarArea('exibicao');
      return;
    }

    let htmlInterno = '';
    // Passa o VALOR (ex: 'academia') para o data attribute
    
    // ✨ CORREÇÃO DO BOTÃO FEIO: Adiciona a classe 'botao-personalizar'
    let botaoPersonalizarHtml = `<button data-nome-perfil="${nomePerfil}" class="botao-personalizar">Personalizar Perfil</button>`;

    // Pega o Label (Ex: 'Academia') para o Título
    let nomeExibicao = nomePerfil; // Fallback
    const optionSelecionada = Array.from(seletorPerfil.options).find(opt => opt.value === nomePerfil);
    if (optionSelecionada) { nomeExibicao = optionSelecionada.text; }


    if (perfil) { // Perfil existe
        let detalhesHtml = '';
        if (perfil.dados_especificos && Object.keys(perfil.dados_especificos).length > 0) {
            
            // Mapeia chaves internas para nomes bonitos
            const MapeamentoNomes = {
                'altura': 'Altura', 'peso': 'Peso', 'nivel_treino': 'Nível', 'local_treino': 'Local', 'freq_treino': 'Frequência', 'objetivo_academia': 'Objetivo Fitness',
                'tipo_estudante': 'Tipo de Estudante', 'area_estudo': 'Área de Estudo', 'periodo_preferido_estudo': 'Período Preferido',
                'area_trabalho': 'Área', 'modalidade_trabalho': 'Modalidade', 'cargo_atual': 'Cargo',
                'objetivo_saude': 'Objetivo de Saúde', 'acompanhamento_medico': 'Acompanhamento Médico', 'restricao_alimentar': 'Restrições',
                'tipo_moradia': 'Moradia', 'tarefa_principal_casa': 'Tarefa Principal', 'mora_sozinho': 'Mora Sozinho(a)',
                'hobby_principal': 'Hobby', 'freq_lazer': 'Frequência de Lazer', 'tipo_lazer_preferido': 'Tipo de Lazer'
            };
            
            detalhesHtml = `<h4>Detalhes Específicos</h4>${
                Object.entries(perfil.dados_especificos)
                      .map(([chave, valor]) => `<p><strong>${MapeamentoNomes[chave] || chave}:</strong> ${valor}</p>`)
                      .join('')
            }`;
        }
        htmlInterno = `<h4>${nomeExibicao}</h4><p><strong>Observações:</strong> ${perfil.detalhes || '(Sem observações)'}</p>${detalhesHtml}${botaoPersonalizarHtml.replace('Personalizar', 'Editar')}`;
    } else { // Perfil não existe
        htmlInterno = `<h4>${nomeExibicao}</h4><p class="perfil-vazio-js" style="text-align: left; padding: 0;">Você ainda não definiu detalhes para este perfil de foco.</p>${botaoPersonalizarHtml}`;
    }
    areaExibicao.innerHTML = htmlInterno;
    mostrarArea('exibicao');
  }

  // === FUNÇÃO preencherFormulario COM LOGS ===
  function preencherFormulario(nomePerfil) {
    console.log("Preenchendo formulário para:", nomePerfil);
    const perfil = perfisDados[nomePerfil];
    console.log("Dados encontrados para este perfil:", perfil); // <-- LOG DOS DADOS COMPLETOS

    if (!formFocoSelect) { console.error("ERRO CRÍTICO: #id_foco_nome_select não encontrado!"); return; }

    const nomePerfilValue = nomePerfil.toLowerCase();
    formFocoSelect.value = nomePerfilValue;
    if (formFocoSelect.value !== nomePerfilValue) { console.warn(`AVISO ao setar formFocoSelect.value para "${nomePerfilValue}"`); }

    // Limpa TODOS os campos
    formDetalhes.value = '';
    [ formAltura, formPeso, formNivelTreino, formLocalTreino, formFreqTreino, formObjetivoAcademia,
      formTipoEstudante, formAreaEstudo, formPeriodoEstudo,
      formAreaTrabalho, formModalidadeTrabalho, formCargoAtual,
      formObjetivoSaude, formAcompanhamento, formRestricao,
      formTipoMoradia, formTarefaCasa, formMoraSozinho,
      formHobby, formFreqLazer, formTipoLazer
    ].forEach(campo => { if (campo) campo.value = ''; });

    // Preenche se houver dados salvos
    if (perfil) {
      console.log("Preenchendo campo 'detalhes'");
      formDetalhes.value = perfil.detalhes || '';
      if (perfil.dados_especificos) {
        const dados = perfil.dados_especificos;
        console.log("Preenchendo com dados_especificos:", dados); // <-- LOG DOS DADOS ESPECÍFICOS

        // Tenta preencher CADA campo e loga o resultado
        try { if (formAltura) { console.log("Tentando preencher altura com:", dados['altura']); formAltura.value = dados['altura'] ?? ''; } } catch(e) { console.error("Erro ao preencher altura:", e); }
        try { if (formPeso) { console.log("Tentando preencher peso com:", dados['peso']); formPeso.value = dados['peso'] ?? ''; } } catch(e) { console.error("Erro ao preencher peso:", e); }
        try { if (formNivelTreino) { console.log("Tentando preencher nivel_treino com:", dados['nivel_treino']); formNivelTreino.value = dados['nivel_treino'] ?? ''; } } catch(e) { console.error("Erro ao preencher nivel_treino:", e); }
        try { if (formLocalTreino) { console.log("Tentando preencher local_treino com:", dados['local_treino']); formLocalTreino.value = dados['local_treino'] ?? ''; } } catch(e) { console.error("Erro ao preencher local_treino:", e); }
        try { if (formFreqTreino) { console.log("Tentando preencher freq_treino com:", dados['freq_treino']); formFreqTreino.value = dados['freq_treino'] ?? ''; } } catch(e) { console.error("Erro ao preencher freq_treino:", e); }
        try { if (formObjetivoAcademia) { console.log("Tentando preencher objetivo_academia com:", dados['objetivo_academia']); formObjetivoAcademia.value = dados['objetivo_academia'] ?? ''; } } catch(e) { console.error("Erro ao preencher objetivo_academia:", e); }
        // Estudos
        try { if (formTipoEstudante) { console.log("Tentando preencher tipo_estudante com:", dados['tipo_estudante']); formTipoEstudante.value = dados['tipo_estudante'] ?? ''; } } catch(e) { console.error("Erro ao preencher tipo_estudante:", e); }
        try { if (formAreaEstudo) { console.log("Tentando preencher area_estudo com:", dados['area_estudo']); formAreaEstudo.value = dados['area_estudo'] ?? ''; } } catch(e) { console.error("Erro ao preencher area_estudo:", e); }
        try { if (formPeriodoEstudo) { console.log("Tentando preencher periodo_preferido_estudo com:", dados['periodo_preferido_estudo']); formPeriodoEstudo.value = dados['periodo_preferido_estudo'] ?? ''; } } catch(e) { console.error("Erro ao preencher periodo_preferido_estudo:", e); }
        // Trabalho
        try { if (formAreaTrabalho) { console.log("Tentando preencher area_trabalho com:", dados['area_trabalho']); formAreaTrabalho.value = dados['area_trabalho'] ?? ''; } } catch(e) { console.error("Erro ao preencher area_trabalho:", e); }
        try { if (formModalidadeTrabalho) { console.log("Tentando preencher modalidade_trabalho com:", dados['modalidade_trabalho']); formModalidadeTrabalho.value = dados['modalidade_trabalho'] ?? ''; } } catch(e) { console.error("Erro ao preencher modalidade_trabalho:", e); }
        try { if (formCargoAtual) { console.log("Tentando preencher cargo_atual com:", dados['cargo_atual']); formCargoAtual.value = dados['cargo_atual'] ?? ''; } } catch(e) { console.error("Erro ao preencher cargo_atual:", e); }
        // Saúde
        try { if (formObjetivoSaude) { console.log("Tentando preencher objetivo_saude com:", dados['objetivo_saude']); formObjetivoSaude.value = dados['objetivo_saude'] ?? ''; } } catch(e) { console.error("Erro ao preencher objetivo_saude:", e); }
        try { if (formAcompanhamento) { console.log("Tentando preencher acompanhamento_medico com:", dados['acompanhamento_medico']); formAcompanhamento.value = dados['acompanhamento_medico'] ?? ''; } } catch(e) { console.error("Erro ao preencher acompanhamento_medico:", e); }
        try { if (formRestricao) { console.log("Tentando preencher restricao_alimentar com:", dados['restricao_alimentar']); formRestricao.value = dados['restricao_alimentar'] ?? ''; } } catch(e) { console.error("Erro ao preencher restricao_alimentar:", e); }
        // Casa
        try { if (formTipoMoradia) { console.log("Tentando preencher tipo_moradia com:", dados['tipo_moradia']); formTipoMoradia.value = dados['tipo_moradia'] ?? ''; } } catch(e) { console.error("Erro ao preencher tipo_moradia:", e); }
        try { if (formTarefaCasa) { console.log("Tentando preencher tarefa_principal_casa com:", dados['tarefa_principal_casa']); formTarefaCasa.value = dados['tarefa_principal_casa'] ?? ''; } } catch(e) { console.error("Erro ao preencher tarefa_principal_casa:", e); }
        try { if (formMoraSozinho) { console.log("Tentando preencher mora_sozinho com:", dados['mora_sozinho']); formMoraSozinho.value = dados['mora_sozinho'] ?? ''; } } catch(e) { console.error("Erro ao preencher mora_sozinho:", e); }
        // Lazer
        try { if (formHobby) { console.log("Tentando preencher hobby_principal com:", dados['hobby_principal']); formHobby.value = dados['hobby_principal'] ?? ''; } } catch(e) { console.error("Erro ao preencher hobby_principal:", e); }
        try { if (formFreqLazer) { console.log("Tentando preencher freq_lazer com:", dados['freq_lazer']); formFreqLazer.value = dados['freq_lazer'] ?? ''; } } catch(e) { console.error("Erro ao preencher freq_lazer:", e); }
        try { if (formTipoLazer) { console.log("Tentando preencher tipo_lazer_preferido com:", dados['tipo_lazer_preferido']); formTipoLazer.value = dados['tipo_lazer_preferido'] ?? ''; } } catch(e) { console.error("Erro ao preencher tipo_lazer_preferido:", e); }

      } else {
         console.log("Perfil existe, mas não tem dados_especificos.");
      }
    } else {
       console.log("Perfil não encontrado nos dados (novo perfil).");
    }

    atualizarPlaceholderDetalhes(nomePerfil);
    toggleCamposEspeciaisFormulario(nomePerfil);
    console.log("Preenchimento do formulário concluído."); // <-- LOG FINAL
  }
  // === FIM DA FUNÇÃO preencherFormulario COM LOGS ===


  function mostrarArea(area) {
    if (!areaExibicao || !secaoFormulario) { console.error("ERRO em mostrarArea."); return; }
    if (area === 'formulario') {
      areaExibicao.style.display = 'none';
      secaoFormulario.style.display = 'block';
      if (form) form.classList.add('editando');
    } else {
      areaExibicao.style.display = 'block';
      secaoFormulario.style.display = 'none';
      if (form) form.classList.remove('editando');
    }
  }

  // --- Event Listeners ---

  if (seletorPerfil) {
    seletorPerfil.addEventListener('change', function () {
      console.log("Dropdown mudou para:", this.value);
      atualizarExibicao(this.value);
      mostrarArea('exibicao');
    });
  }

  if (containerDinamico) {
    containerDinamico.addEventListener('click', function(event) {
      if (areaExibicao.contains(event.target) && event.target.classList.contains('botao-personalizar')) {
        console.log("Botão Personalizar/Editar clicado!");
        const nomePerfil = event.target.getAttribute('data-nome-perfil');
        if (nomePerfil) {
          preencherFormulario(nomePerfil);
          mostrarArea('formulario');
        } else { console.error("ERRO: Botão sem data-nome-perfil."); }
      }
    });
  }

  if (botaoCancelar) {
    botaoCancelar.addEventListener('click', function() {
      console.log("Botão Cancelar clicado!");
      atualizarExibicao(perfilSelecionadoAtual);
    });
  }

   if (formFocoSelect) {
       formFocoSelect.addEventListener('change', function() {
           console.log("Select do formulário mudou para:", this.value);
           atualizarPlaceholderDetalhes(this.value);
           toggleCamposEspeciaisFormulario(this.value);
       });
   }

  // --- Inicialização ---
  console.log("Inicializando...");
  mostrarArea('exibicao');
  if (formFocoSelect) {
       atualizarPlaceholderDetalhes(formFocoSelect.value);
       toggleCamposEspeciaisFormulario(formFocoSelect.value);
   }
  console.log("Inicialização completa.");

});