const STORAGE_KEY = 'cyberbackup-theme';

export class ThemeManager {
  constructor(toggleButton) {
    this.toggleButton = toggleButton;
    this.root = document.documentElement;
    this.current = this.#load() || 'theme-dark';
    this.apply(this.current);

    if (this.toggleButton) {
      this.toggleButton.addEventListener('click', () => this.toggle());
      this.#updateLabel();
    }
  }

  toggle() {
    this.current = this.current === 'theme-dark' ? 'theme-light' : 'theme-dark';
    this.apply(this.current);
    this.#save(this.current);
    this.#updateLabel();
  }

  apply(themeClass) {
    this.root.classList.remove('theme-dark', 'theme-light');
    this.root.classList.add(themeClass);
  }

  #updateLabel() {
    if (!this.toggleButton) return;
    const isLight = this.current === 'theme-light';
    this.toggleButton.textContent = isLight ? '🌙 Dark mode' : '☀️ Light mode';
    this.toggleButton.setAttribute('aria-label', `Switch to ${isLight ? 'dark' : 'light'} mode`);
  }

  #save(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      console.warn('Failed to persist theme preference', error);
    }
  }

  #load() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  }
}
