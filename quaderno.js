document.getElementById("signature-year").textContent = new Date().getFullYear();
(() => {
  function initialize(root) {
    const viewport = root.querySelector('.carousel-window');
    const track = root.querySelector('.carousel-track');
    const previous = root.querySelector('[data-previous]');
    const next = root.querySelector('[data-next]');
    const play = root.querySelector('[data-play]');
    const counter = root.querySelector('[data-current]');
    const status = root.querySelector('[data-status]');
    const playLabel = play?.querySelector('[data-play-label]');
    const slides = track ? Array.from(track.children).filter(el => el.matches('.example-slide')) : [];

    if (!viewport || !previous || !next || !play || slides.length < 3) return;

    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const cycle = index => (index + slides.length) % slides.length;
    const middle = 'translateX(-100%)';
    let current = 0;
    let playing = !motion.matches;
    let timer;
    let animation;
    let touch;

    function seatSlides() {
      // One panel before the current one, the current panel, then its successors.
      slides.forEach((slide, i) => {
        slide.style.order = cycle(i - current + 1);
      });
      track.style.transform = middle;
    }

    function markCurrent() {
      slides.forEach((slide, i) => {
        slide.inert = i !== current;
        slide.setAttribute('aria-hidden', String(i !== current));
      });
      if (counter) counter.textContent = String(current + 1);
    }

    function settle() {
      if (!animation) return;
      animation.onfinish = null;
      seatSlides();
      animation.cancel();
      animation = null;
    }

    function schedule() {
      window.clearTimeout(timer);
      if (playing && !document.hidden && !touch) {
        timer = window.setTimeout(() => move(1, false), 5000);
      }
    }

    function setPlaying(value) {
      playing = value;
      const label = playing ? 'Pausa' : 'Riproduci';
      play.dataset.playing = String(playing);
      play.setAttribute('aria-label', playing ? 'Pausa, ferma lo scorrimento automatico' : 'Riproduci gli esempi in automatico');
      play.title = playing ? 'Ferma lo scorrimento automatico' : 'Avvia lo scorrimento automatico';
      if (playLabel) playLabel.textContent = label;
      schedule();
    }

    function move(direction, manual) {
      settle();
      if (manual) setPlaying(false);
      current = cycle(current + direction);
      markCurrent();
      if (manual && status) {
        const name = slides[current].dataset.title;
        status.textContent = 'Esempio ' + (current + 1) + ' di ' + slides.length + (name ? '. ' + name : '.');
      }
      if (motion.matches || typeof track.animate !== 'function') {
        seatSlides();
      } else {
        const end = direction === 1 ? 'translateX(-200%)' : 'translateX(0%)';
        animation = track.animate([{ transform: middle }, { transform: end }], {
          duration: 340,
          easing: 'cubic-bezier(.25,.7,.2,1)',
          fill: 'forwards'
        });
        animation.onfinish = settle;
      }
      schedule();
    }

    previous.addEventListener('click', () => move(-1, true));
    next.addEventListener('click', () => move(1, true));
    play.addEventListener('click', () => setPlaying(!playing));
    root.addEventListener('keydown', event => {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      move(event.key === 'ArrowLeft' ? -1 : 1, true);
    });

    viewport.addEventListener('pointerdown', event => {
      if (!event.isPrimary || event.button !== 0) return;
      touch = { id: event.pointerId, x: event.clientX, y: event.clientY };
      schedule();
      viewport.setPointerCapture(event.pointerId);
    });

    function endGesture(event) {
      if (!touch || touch.id !== event.pointerId) return;
      const dx = event.clientX - touch.x;
      const dy = event.clientY - touch.y;
      touch = null;
      if (event.type === 'pointerup' && Math.abs(dx) >= 32 && Math.abs(dx) > 1.3 * Math.abs(dy)) {
        move(dx < 0 ? 1 : -1, true);
      } else {
        schedule();
      }
    }
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(type => viewport.addEventListener(type, endGesture));

    document.addEventListener('visibilitychange', () => {
      touch = null;
      settle();
      schedule();
    });
    motion.addEventListener('change', () => {
      if (motion.matches) {
        settle();
        setPlaying(false);
      }
    });
    if (status) {
      status.setAttribute('aria-live', 'polite');
      status.setAttribute('aria-atomic', 'true');
    }
    seatSlides();
    markCurrent();
    setPlaying(playing);
  }

  function start() {
    document.querySelectorAll('.carousel').forEach(initialize);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
