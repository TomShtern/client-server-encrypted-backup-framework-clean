const DEFAULT_DURATION = 4000;

export class ToastManager {
  #stack;
  #activeToasts;

  constructor(stackElement) {
    this.#stack = stackElement;
    this.#activeToasts = new Set();
  }

  show(message, variant = 'info', duration = DEFAULT_DURATION) {
    if (!this.#stack) {
      return () => {};
    }
    const toast = document.createElement('div');
    toast.className = `toast ${variant}`;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.textContent = message;
    this.#stack.append(toast);
    this.#activeToasts.add(toast);

    const close = () => {
      if (!this.#activeToasts.has(toast)) {
        return;
      }
      this.#activeToasts.delete(toast);
      toast.classList.add('closing');
      toast.addEventListener('transitionend', () => toast.remove(), { once: true });
      // Fallback removal
      setTimeout(() => toast.remove(), 300);
    };

    if (duration > 0) {
      setTimeout(close, duration);
    }

    return close;
  }

  clear() {
    for (const toast of this.#activeToasts) {
      toast.remove();
    }
    this.#activeToasts.clear();
  }
}
