// AIOS — site.js
// Animações de revelação, contadores e interações ao estilo obscura.sh

document.documentElement.classList.add('js');

// ---------------------------------------------------------------
// Scroll reveal — IntersectionObserver com easing cubic-bezier obscura
// ---------------------------------------------------------------
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

// ---------------------------------------------------------------
// Contadores animados — elementos com [data-count]
// ---------------------------------------------------------------
function animateCount(el) {
  const target = parseInt(el.dataset.count, 10);
  if (isNaN(target)) return;
  const prefix = el.dataset.prefix || '';
  const suffix = el.dataset.suffix || '';
  const duration = 1400;
  const start = performance.now();

  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    // easeOutExpo — mesmo feeling do obscura.sh
    const ease = t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    const value = Math.round(target * ease);
    el.textContent = `${prefix}${value}${suffix}`;
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

const counters = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      animateCount(entry.target);
      counters.unobserve(entry.target);
    }
  });
}, { threshold: 0.6 });

document.querySelectorAll('[data-count]').forEach((el) => counters.observe(el));

// ---------------------------------------------------------------
// Menu mobile
// ---------------------------------------------------------------
const navToggle = document.getElementById('navToggle');
const mnav = document.getElementById('mnav');
if (navToggle && mnav) {
  navToggle.addEventListener('click', () => {
    const open = mnav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // Fecha ao clicar em link
  mnav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => {
    mnav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
  }));
}

// ---------------------------------------------------------------
// Header: escurece/blur ao rolar
// ---------------------------------------------------------------
const nav = document.getElementById('nav');
let lastY = 0;
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (y > 24) {
    nav.style.background = 'rgba(0,0,0,.82)';
    nav.style.borderBottom = '1px solid var(--line)';
    nav.style.backdropFilter = 'blur(16px)';
  } else {
    nav.style.background = 'transparent';
    nav.style.borderBottom = '1px solid transparent';
    nav.style.backdropFilter = 'none';
  }
  lastY = y;
}, { passive: true });

// ---------------------------------------------------------------
// Smooth scroll para âncoras
// ---------------------------------------------------------------
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href');
    if (id.length < 2) return;
    const target = document.querySelector(id);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
