const STORAGE_KEYS = {
  chunk: 'cyberbackup-chunk-size',
  retry: 'cyberbackup-retry-limit',
};

const DEFAULTS = {
  chunkSize: 8,
  retryLimit: 3,
};

const LIMITS = {
  chunkSize: { min: 1, max: 256 },
  retryLimit: { min: 0, max: 20 },
};

function clamp(value, { min, max }) {
  return Math.min(Math.max(value, min), max);
}

function parseNumericInput(input, { min, max }) {
  const raw = input.value.trim();
  if (raw.length === 0) {
    return null;
  }
  const numeric = Number.parseInt(raw, 10);
  if (!Number.isFinite(numeric)) {
    return null;
  }
  return clamp(numeric, { min, max });
}

export class AdvancedSettings {
  constructor({ chunkInput, retryInput, resetButton, toast, announcer }) {
    this.chunkInput = chunkInput;
    this.retryInput = retryInput;
    this.resetButton = resetButton;
    this.toast = toast;
    this.announcer = announcer;

    this.#hydrate();
    this.#bindEvents();
  }

  getOptions() {
    const chunk = parseNumericInput(this.chunkInput, LIMITS.chunkSize);
    const retry = parseNumericInput(this.retryInput, LIMITS.retryLimit);
    const options = {};

    if (chunk !== null) {
      options.chunk_size_mb = chunk;
    }

    if (retry !== null) {
      options.retry_limit = retry;
    }

    return options;
  }

  reset() {
    this.#applyValue(this.chunkInput, DEFAULTS.chunkSize, STORAGE_KEYS.chunk);
    this.#applyValue(this.retryInput, DEFAULTS.retryLimit, STORAGE_KEYS.retry);
    this.toast?.show('Advanced settings restored to defaults', 'info', 2200);
    this.announcer?.announce('Advanced settings reset to defaults');
  }

  #hydrate() {
    this.#applyValue(this.chunkInput, this.#loadFromStorage(STORAGE_KEYS.chunk, DEFAULTS.chunkSize));
    this.#applyValue(this.retryInput, this.#loadFromStorage(STORAGE_KEYS.retry, DEFAULTS.retryLimit));
  }

  #applyValue(input, value, storageKey) {
    if (!input) {
      return;
    }
    input.value = value.toString();
    input.setAttribute('aria-invalid', 'false');
    if (storageKey) {
      this.#persist(storageKey, value);
    }
  }

  #bindEvents() {
    if (this.resetButton) {
      this.resetButton.addEventListener('click', () => this.reset());
    }

    if (this.chunkInput) {
      this.chunkInput.addEventListener('blur', () => this.#validateAndPersist(this.chunkInput, STORAGE_KEYS.chunk, LIMITS.chunkSize));
    }

    if (this.retryInput) {
      this.retryInput.addEventListener('blur', () => this.#validateAndPersist(this.retryInput, STORAGE_KEYS.retry, LIMITS.retryLimit));
    }
  }

  #validateAndPersist(input, storageKey, limits) {
    if (!input) {
      return;
    }

    const parsed = parseNumericInput(input, limits);
    if (parsed === null) {
      input.setAttribute('aria-invalid', 'true');
      this.toast?.show(`Enter a value between ${limits.min} and ${limits.max}`, 'warn', 3200);
      this.announcer?.announce(`Invalid value. Enter a number between ${limits.min} and ${limits.max}`);
      return;
    }

    input.value = parsed.toString();
    input.setAttribute('aria-invalid', 'false');
    this.#persist(storageKey, parsed);
  }

  #persist(key, value) {
    try {
      localStorage.setItem(key, value.toString());
    } catch (error) {
      console.warn('Failed to persist advanced setting', { key, error });
    }
  }

  #loadFromStorage(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      if (value === null) {
        return fallback;
      }
      const numeric = Number.parseInt(value, 10);
      return Number.isFinite(numeric) ? clamp(numeric, LIMITS[key === STORAGE_KEYS.chunk ? 'chunkSize' : 'retryLimit']) : fallback;
    } catch {
      return fallback;
    }
  }
}
