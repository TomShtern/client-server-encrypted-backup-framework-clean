// Optimized shallow clone for primitive values and simple objects
function shallowClone(value) {
  if (value === null || typeof value !== 'object') {
    return value;
  }

  if (Array.isArray(value)) {
    return [...value];
  }

  return { ...value };
}

// Deep equality check to avoid unnecessary updates
function shallowEqual(objA, objB) {
  if (objA === objB) return true;
  if (typeof objA !== 'object' || typeof objB !== 'object' || objA === null || objB === null) {
    return false;
  }

  const keysA = Object.keys(objA);
  const keysB = Object.keys(objB);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (objA[key] !== objB[key]) return false;
  }

  return true;
}

export class StateStore {
  #state;
  #listeners;
  #pendingUpdate;
  #updateScheduled;

  constructor(initialState) {
    this.#state = shallowClone(initialState);
    this.#listeners = new Set();
    this.#pendingUpdate = null;
    this.#updateScheduled = false;
  }

  get snapshot() {
    // Return direct reference for reads (caller shouldn't mutate)
    // This avoids expensive deep cloning on every read
    return this.#state;
  }

  update(patch) {
    // Batch updates using requestAnimationFrame
    if (!this.#pendingUpdate) {
      this.#pendingUpdate = {};
    }

    Object.assign(this.#pendingUpdate, patch);

    if (!this.#updateScheduled) {
      this.#updateScheduled = true;
      requestAnimationFrame(() => this.#flushUpdate());
    }
  }

  #flushUpdate() {
    if (!this.#pendingUpdate) {
      this.#updateScheduled = false;
      return;
    }

    const next = { ...this.#state, ...this.#pendingUpdate };

    // Only notify if state actually changed
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }

    this.#pendingUpdate = null;
    this.#updateScheduled = false;
  }

  // Force immediate update without batching (use sparingly)
  updateImmediate(patch) {
    const next = { ...this.#state, ...patch };
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }

  mutate(mutator) {
    const next = { ...this.#state };
    mutator(next);

    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }

  #notifyListeners(state) {
    // Use microtask queue for listener notifications
    queueMicrotask(() => {
      for (const listener of this.#listeners) {
        try {
          listener(state);
        } catch (error) {
          console.error('State listener error:', error);
        }
      }
    });
  }

  subscribe(listener) {
    if (typeof listener !== 'function') {
      throw new TypeError('Listener must be a function');
    }
    this.#listeners.add(listener);

    // Initial notification
    queueMicrotask(() => listener(this.#state));

    return () => this.#listeners.delete(listener);
  }
}
