/**
 * MedAnalyzer AI — Theme Toggle (Light/Dark Mode)
 */
(function() {
  const THEME_KEY = 'medanalyzer-theme';
  const html = document.documentElement;
  const toggleBtn = document.getElementById('themeToggle');

  // Load saved theme or default to light
  const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
  html.setAttribute('data-theme', savedTheme);
  updateIcon(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem(THEME_KEY, next);
      updateIcon(next);
    });
  }

  function updateIcon(theme) {
    if (!toggleBtn) return;
    const icon = toggleBtn.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
    }
  }
})();
