(function () {
  const modal = document.getElementById('loginModal');
  const openBtn = document.getElementById('btnOpenLogin');
  if (!modal || !openBtn) return;

  function openLogin() {
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.getElementById('loginEmail')?.focus();
  }

  function closeLogin() {
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
  }

  openBtn.addEventListener('click', openLogin);

  modal.querySelectorAll('[data-close-login]').forEach(el => {
    el.addEventListener('click', closeLogin);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) closeLogin();
  });
})();