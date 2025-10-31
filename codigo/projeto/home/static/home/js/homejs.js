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
        profileDropdownMobile.classList.remove("aberto");
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
    // Fecha dropdown desktop
    if (profileDropdown && !profileDropdown.contains(e.target) && !dropdownTrigger.contains(e.target)) {
      profileDropdown.classList.remove("aberto");
    }
    
    // Dropdown mobile não precisa, pois está dentro do overlay
  });

  
  // --- [NOVO] LÓGICA DA API DE RESGATAR FOCO ---
  
  const btnResgatar = document.getElementById("btn-resgatar-foco");
  
  // Pega os dados JSON que colocamos no HTML
  const jsDataElement = document.getElementById("js-data");
  const jsData = JSON.parse(jsDataElement.textContent);
  const resgatarFocoUrl = jsData.resgatarFocoUrl;
  const csrfToken = jsData.csrfToken;

  if (btnResgatar) {
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
        // O body pode ser vazio, já que o backend só precisa do POST
        body: JSON.stringify({}), 
      })
      .then(response => {
        if (!response.ok) {
          // Se o servidor retornar um erro (ex: 400, 405), pega a mensagem
          return response.json().then(err => {
             throw new Error(err.message || 'Erro de rede');
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // --- A MÁGICA ACONTECE AQUI ---
          
          // 1. Atualiza os stats do sidebar
          document.getElementById("xp-total-display").textContent = data.xp_atual;
          document.getElementById("dias-foco-display").textContent = data.dias_foco;

          // 2. Atualiza as "bolinhas" de nível
          //    (QuerySelectorAll pega TODAS, desktop e mobile)
          document.querySelectorAll(".level-badge-display").forEach(badge => {
            badge.textContent = data.nivel;
          });

          // 3. Atualiza o card de "Evolução"
          document.getElementById("progresso-level-texto").textContent = `Progresso Nível ${data.nivel}`;
          document.getElementById("progresso-xp-atual").textContent = `${data.xp_atual} XP`;
          document.getElementById("progresso-xp-necessario").textContent = `${data.xp_proximo_nivel} XP`;

          // 4. Calcula e atualiza a barra de progresso
          let percentual = 0;
          if (data.xp_proximo_nivel > 0) { // Evita divisão por zero
            percentual = (data.xp_atual / data.xp_proximo_nivel) * 100;
          }
          percentual = Math.min(percentual, 100); // Garante que não passe de 100%

          const barra = document.getElementById("progresso-barra-preenchimento");
          barra.style.width = `${percentual}%`;
          barra.textContent = `${percentual.toFixed(0)}%`;

          // 5. Atualiza o botão
          btnResgatar.textContent = "Foco resgatado!";
          // O botão já está desabilitado e assim permanecerá
          
        } else {
          // Caso o 'success' seja false (ex: "já resgatou hoje")
          throw new Error(data.message || "Não foi possível resgatar.");
        }
      })
      .catch(error => {
        // Em caso de erro de rede ou erro do 'throw new Error'
        console.error("Erro ao resgatar foco:", error);
        alert(`Erro: ${error.message}`);
        // Re-habilita o botão se falhar, exceto se for "já resgatou"
        if (error.message.includes("já resgatou")) {
             btnResgatar.textContent = "Foco resgatado!";
             btnResgatar.disabled = true;
        } else {
            btnResgatar.textContent = "Resgatar Foco (20xp)";
            btnResgatar.disabled = false;
        }
      });
    });
  }

});