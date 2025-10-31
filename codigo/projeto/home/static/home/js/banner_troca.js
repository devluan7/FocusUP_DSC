let currentIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
  const cardsContainer = document.querySelector('.div_cards'); // container dos cards
  const cards = document.querySelectorAll('.card_ativo');
  let dotsContainer = document.createElement('div');
  dotsContainer.classList.add('carousel_dots');
  cardsContainer.after(dotsContainer);

  // Cria bolinhas
  cards.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.classList.add('dot');
    if (i === currentIndex) dot.classList.add('active');
    dot.addEventListener('click', () => {
      currentIndex = i;
      showCard();
    });
    dotsContainer.appendChild(dot);
  });

  showCard();

  let startX = 0;
  let endX = 0;
  let isDragging = false;

  // Touch events (mobile)
  cardsContainer.addEventListener('touchstart', e => startX = e.touches[0].clientX);
  cardsContainer.addEventListener('touchend', e => {
    endX = e.changedTouches[0].clientX;
    handleSwipe();
  });

  // Mouse events (desktop, só para teste mobile)
  cardsContainer.addEventListener('mousedown', e => {
    isDragging = true;
    startX = e.clientX;
  });
  cardsContainer.addEventListener('mouseup', e => {
    if(!isDragging) return;
    isDragging = false;
    endX = e.clientX;
    handleSwipe();
  });

  function handleSwipe() {
    const threshold = 50; // distância mínima para considerar swipe
    if (endX - startX > threshold) {
      // swipe para a direita → card anterior
      currentIndex = (currentIndex - 1 + cards.length) % cards.length;
    } else if (startX - endX > threshold) {
      // swipe para a esquerda → próximo card
      currentIndex = (currentIndex + 1) % cards.length;
    }
    showCard();
  }

  function showCard() {
    cards.forEach((card, i) => card.classList.toggle('hidden', i !== currentIndex));
    const dots = dotsContainer.querySelectorAll('.dot');
    dots.forEach((d, i) => d.classList.toggle('active', i === currentIndex));
  }
});
