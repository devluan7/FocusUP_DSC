document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const menuMobile = document.getElementById("menuMobile");

  if (menuBtn && menuMobile) {
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // previne conflito com clique fora
      menuMobile.classList.toggle("active");
    });

    // Fecha ao clicar fora
    document.addEventListener("click", (e) => {
      if (
        menuMobile.classList.contains("active") &&
        !menuMobile.contains(e.target) &&
        e.target !== menuBtn
      ) {
        menuMobile.classList.remove("active");
      }
    });

    // Fecha ao rolar a página
    window.addEventListener("scroll", () => {
      if (menuMobile.classList.contains("active")) {
        menuMobile.classList.remove("active");
      }
    });
  }
});
