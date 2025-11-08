const LEVEL_PRIORITY = new Set(['info', 'warn', 'error']);

function normalizeLevel(level) {
  if (!level) return 'info';
  const normalized = level.toString().toLowerCase();
  if (LEVEL_PRIORITY.has(normalized)) {
    return normalized;
  }
  return 'info';
}

export class LogStore {
  #entries;
  #filter;
  #autoScroll;
  #container;

  constructor(container) {
    this.#entries = [];
    this.#filter = 'all';
    this.#autoScroll = true;
    this.#container = container;
  }

  setFilter(filter) {
    this.#filter = filter;
    this.render();
  }

  setAutoScroll(enabled) {
    this.#autoScroll = Boolean(enabled);
  }

  add(message, { level = 'info', phase, timestamp = new Date() } = {}) {
    const entry = {
      timestamp: timestamp instanceof Date ? timestamp : new Date(timestamp),
      message,
      phase: phase || null,
      level: normalizeLevel(level),
    };
    this.#entries.push(entry);
    if (this.#entries.length > 500) {
      this.#entries.splice(0, this.#entries.length - 500);
    }
    this.render();
  }

  export() {
    const lines = [];
    for (const entry of this.#entries) {
      const iso = entry.timestamp.toISOString();
      const phase = entry.phase ? `[${entry.phase}] ` : '';
      lines.push(`${iso} [${entry.level.toUpperCase()}] ${phase}${entry.message}`);
    }
    return lines.join('\n');
  }

  render() {
    if (!this.#container) return;
    const fragment = document.createDocumentFragment();
    const filter = this.#filter;
    const filteredEntries = this.#entries.filter((entry) => filter === 'all' || entry.level === filter);

    for (const entry of filteredEntries.slice(-400)) {
      const line = document.createElement('div');
      line.dataset.level = entry.level;
      line.textContent = `${entry.timestamp.toLocaleTimeString()} — ${entry.message}`;
      fragment.append(line);
    }

    this.#container.replaceChildren(fragment);

    if (this.#autoScroll) {
      this.#container.scrollTop = this.#container.scrollHeight;
    }
  }
}
