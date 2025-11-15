// Espera o documento carregar antes de rodar o script
document.addEventListener("DOMContentLoaded", function () {
  
  // --- LÓGICA DE MENUS E DROPDOWNS ---
  
  // Elementos do Menu Mobile
  const botaoMenuMobile = document.getElementById("botao-menu-mobile");
  const menuMobileOverlay = document.getElementById("menu-mobile-overlay");
  
  // Elementos do Dropdown (Desktop)
  const dropdownTrigger = document.getElementById("profile-dropdown-trigger");
  const profileDropdown = document.getElementById("profile-dropdown");
  
  // Elementos do Dropdown (Mobile)
  const dropdownTriggerMobile = document.getElementById("profile-dropdown-trigger-mobile");
  const profileDropdownMobile = document.getElementById("profile-dropdown-mobile");

  // Abrir/Fechar Menu Mobile
  if (botaoMenuMobile && menuMobileOverlay) {
    botaoMenuMobile.addEventListener("click", () => {
      botaoMenuMobile.classList.toggle("aberto");
      menuMobileOverlay.classList.toggle("aberto");
      document.body.classList.toggle("menu-aberto-sem-scroll");
      
      // Fechar dropdowns internos se o menu fechar
      if (!menuMobileOverlay.classList.contains("aberto")) {
        // Verifica se o dropdown mobile existe antes de fechar
        if (profileDropdownMobile) {
          profileDropdownMobile.classList.remove("aberto");
        }
      }
    });
  }

  // Abrir/Fechar Dropdown (Desktop)
  if (dropdownTrigger && profileDropdown) {
    dropdownTrigger.addEventListener("click", (e) => {
      e.stopPropagation(); // Impede que o clique feche o menu imediatamente
      profileDropdown.classList.toggle("aberto");
    });
  }

  // Abrir/Fechar Dropdown (Mobile)
  if (dropdownTriggerMobile && profileDropdownMobile) {
    dropdownTriggerMobile.addEventListener("click", (e) => {
      e.stopPropagation();
      profileDropdownMobile.classList.toggle("aberto");
    });
  }

  // Fechar menus clicando fora
  document.addEventListener("click", (e) => {
    
    // Adiciona verificação se dropdownTrigger existe (&& dropdownTrigger)
    if (profileDropdown && !profileDropdown.contains(e.target) && dropdownTrigger && !dropdownTrigger.contains(e.target)) {
      profileDropdown.classList.remove("aberto");
    }
    
  });

  
  // --- LÓGICA DA API DE RESGATAR FOCO ---
  
  const btnResgatar = document.getElementById("btn-resgatar-foco");
  const jsDataElement = document.getElementById("js-data"); // Pega o elemento
  
  // O script SÓ TENTA ler o JSON se o elemento #js-data existir.
  // Isso impede o crash em outras páginas (como lista_tarefas).
  if (btnResgatar && jsDataElement) {
  
    // Move o parse para DENTRO do 'if'
    const jsData = JSON.parse(jsDataElement.textContent);
    const resgatarFocoUrl = jsData.resgatarFocoUrl;
    const csrfToken = jsData.csrfToken;

    btnResgatar.addEventListener("click", function () {
      
      // Desativa o botão para evitar cliques duplos
      btnResgatar.disabled = true;
      btnResgatar.textContent = "Processando...";

      fetch(resgatarFocoUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken, // Envia o CSRF token
        },
        body: JSON.stringify({}), 
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(err => {
              throw new Error(err.message || 'Erro de rede');
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          
          // --- MUDANÇA: Chama a nova função para atualizar o XP ---
          // "Traduz" os nomes das variáveis do 'resgatar' para
          // os nomes que a função 'atualizarBarraDeXP' espera.
          const dadosFormatados = {
              nivel_usuario: data.nivel,
              xp_total_usuario: data.xp_atual,
              xp_proximo_nivel: data.xp_proximo_nivel
          };
          // Chama a função que agora é reutilizável
          atualizarBarraDeXP(dadosFormatados);
          // ---------------------------------------------------

          // Atualiza os campos específicos do Resgate (Streak)
          const diasFocoDisplay = document.getElementById("dias-foco-display");
          if (diasFocoDisplay) diasFocoDisplay.textContent = data.dias_foco;
          
          btnResgatar.textContent = "Foco resgatado!";
          
        } else {
          throw new Error(data.message || "Não foi possível resgatar.");
        }
      })
      .catch(error => {
        console.error("Erro ao resgatar foco:", error);
        alert(`Erro: ${error.message}`);
        
        if (error.message.includes("já resgatou")) {
             btnResgatar.textContent = "Foco resgatado!";
             btnResgatar.disabled = true;
        } else {
             btnResgatar.textContent = "Resgatar Foco (20xp)";
             btnResgatar.disabled = false;
        }
      });
    });
  } // Fim do 'if (btnResgatar && jsDataElement)'


  // -----------------------------------------------------------------
  // --- FUNÇÃO DE XP (REORGANIZADA) ---
  // Esta é a sua lógica de XP, agora movida para uma função separada
  // para que o 'lista_tarefas_ai.js' possa chamá-la.
  // -----------------------------------------------------------------
  function atualizarBarraDeXP(data) {
      console.log("homejs.js: Recebido comando para atualizar a barra de XP.");
      console.log(data); // Mostra os dados recebidos

      // 1. Atualiza as "bolinhas" de nível (desktop e mobile)
      const badgesNivel = document.querySelectorAll(".level-badge-display");
      if (badgesNivel.length > 0 && data.nivel_usuario !== undefined) {
          badgesNivel.forEach(badge => {
              badge.textContent = data.nivel_usuario;
          });
          console.log(`Nível atualizado para: ${data.nivel_usuario}`);
      } else {
          console.warn("Elementos '.level-badge-display' não encontrados ou 'data.nivel_usuario' faltando.");
      }
      
      // 2. Atualiza o card de "Evolução" (se estiver na página 'home')
      const progressoLevelTexto = document.getElementById("progresso-level-texto");
      const progressoXpAtual = document.getElementById("progresso-xp-atual");
      const progressoXpNecessario = document.getElementById("progresso-xp-necessario");
      const barraPreenchimento = document.getElementById("progresso-barra-preenchimento");

      // Verifica se os dados necessários existem antes de tentar usá-los
      if (data.xp_total_usuario !== undefined && data.xp_proximo_nivel !== undefined && data.nivel_usuario !== undefined) {
          if (progressoLevelTexto && progressoXpAtual && progressoXpNecessario && barraPreenchimento) {
              
              progressoLevelTexto.textContent = `Progresso Nível ${data.nivel_usuario}`;
              progressoXpAtual.textContent = `${data.xp_total_usuario} XP`;
              progressoXpNecessario.textContent = `${data.xp_proximo_nivel} XP`;

              // Calcula e atualiza a barra de progresso
              let percentual = 0;
              if (data.xp_proximo_nivel > 0) { // Evita divisão por zero
                  percentual = (data.xp_total_usuario / data.xp_proximo_nivel) * 100;
              }
              percentual = Math.min(percentual, 100); // Garante que não passe de 100%

              barraPreenchimento.style.width = `${percentual}%`;
              barraPreenchimento.textContent = `${percentual.toFixed(0)}%`;
              
              console.log(`Barra de progresso (home) atualizada para: ${percentual.toFixed(0)}%`);
          }
      } else {
          console.warn("Dados de XP/Nível ausentes no objeto 'data', barra de progresso não atualizada.");
      }

      // 3. Atualiza os stats do sidebar (se estiver na página 'home')
      const xpTotalDisplay = document.getElementById("xp-total-display");
      if (xpTotalDisplay && data.xp_total_usuario !== undefined) {
          xpTotalDisplay.textContent = data.xp_total_usuario;
          console.log(`Sidebar XP (home) atualizado para: ${data.xp_total_usuario}`);
      }
  }
  // --- FIM DA FUNÇÃO ADICIONADA ---

}); // <-- Este '});' é o fechamento do seu DOMContentLoaded