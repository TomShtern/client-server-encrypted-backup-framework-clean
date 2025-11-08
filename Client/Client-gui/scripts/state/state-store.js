function cloneFallback(value) {
  if (value === null || typeof value !== 'object') {
    return value;
  }

  if (value instanceof Date) {
    return new Date(value.getTime());
  }

  if (Array.isArray(value)) {
    return value.map((item) => cloneFallback(item));
  }

  const result = {};
  for (const [key, entry] of Object.entries(value)) {
    result[key] = cloneFallback(entry);
  }
  return result;
}

function deepClone(value) {
  if (typeof globalThis.structuredClone === 'function') {
    return globalThis.structuredClone(value);
  }
  return cloneFallback(value);
}

export class StateStore {
  #state;
  #listeners;

  constructor(initialState) {
    this.#state = deepClone(initialState);
    this.#listeners = new Set();
  }

  get snapshot() {
    return deepClone(this.#state);
  }

  update(patch) {
    const next = { ...this.#state, ...patch };
    this.#state = next;
    for (const listener of this.#listeners) {
      listener(next);
    }
  }

  mutate(mutator) {
    const next = deepClone(this.#state);
    mutator(next);
    this.#state = next;
    for (const listener of this.#listeners) {
      listener(next);
    }
  }

  subscribe(listener) {
    if (typeof listener !== 'function') {
      throw new TypeError('Listener must be a function');
    }
    this.#listeners.add(listener);
    listener(this.#state);
    return () => this.#listeners.delete(listener);
  }
}
