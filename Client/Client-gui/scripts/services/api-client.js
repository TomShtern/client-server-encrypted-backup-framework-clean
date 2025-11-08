const DEFAULT_TIMEOUT = 20000;

function withTimeout(promise, timeoutMs = DEFAULT_TIMEOUT) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timed out')), timeoutMs);
    }),
  ]);
}

function normalizeResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  return (isJson ? response.json() : response.text()).then((payload) => ({ response, payload }));
}

export class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  #buildUrl(path) {
    if (!path.startsWith('/')) {
      return `${this.baseUrl}/${path}`;
    }
    return `${this.baseUrl}${path}`;
  }

  async health() {
    const { response, payload } = await withTimeout(
      fetch(this.#buildUrl('/api/health'), {
        headers: { 'Cache-Control': 'no-cache' },
      }),
      8000,
    ).then(normalizeResponse);
    if (!response.ok) {
      throw new Error(payload?.error || 'Health check failed');
    }
    return payload;
  }

  async connect(config) {
    const body = JSON.stringify(config);
    const { response, payload } = await withTimeout(
      fetch(this.#buildUrl('/api/connect'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      }),
    ).then(normalizeResponse);
    if (!response.ok || !payload?.success) {
      throw new Error(payload?.error || payload?.message || 'Failed to connect');
    }
    return payload;
  }

  async disconnect() {
    const { response, payload } = await withTimeout(
      fetch(this.#buildUrl('/api/disconnect'), { method: 'POST' }),
    ).then(normalizeResponse);
    if (!response.ok || !payload?.success) {
      throw new Error(payload?.error || 'Failed to disconnect');
    }
    return payload;
  }

  async startBackup({ file, username, host, port, options = {} }) {
    if (!(file instanceof File)) {
      throw new TypeError('A valid file must be provided');
    }
    const form = new FormData();
    form.append('file', file, file.name);
    if (username) form.append('username', username);
    if (host) form.append('host', host);
    if (port) form.append('port', String(port));

    for (const [key, value] of Object.entries(options)) {
      if (value === undefined || value === null || value === '') return;
      form.append(key, String(value));
    }

    const { response, payload } = await withTimeout(
      fetch(this.#buildUrl('/api/start_backup'), {
        method: 'POST',
        body: form,
      }),
      60000,
    ).then(normalizeResponse);
    if (!response.ok || !payload?.success) {
      throw new Error(payload?.error || payload?.message || 'Backup start failed');
    }
    return payload;
  }

  async status(jobId) {
    const origin = globalThis.location?.origin ?? 'http://localhost';
    const url = new URL(this.#buildUrl('/api/status'), origin);
    if (jobId) {
      url.searchParams.set('job_id', jobId);
    }
    const { response, payload } = await withTimeout(
      fetch(url.toString(), { headers: { 'Cache-Control': 'no-cache' } }),
      10000,
    ).then(normalizeResponse);
    if (!response.ok) {
      throw new Error(payload?.error || 'Status request failed');
    }
    return payload;
  }

  async pause() {
    return this.#command('/api/pause');
  }

  async resume() {
    return this.#command('/api/resume');
  }

  async stop() {
    return this.#command('/api/stop');
  }

  #command(path) {
    return withTimeout(fetch(this.#buildUrl(path), { method: 'POST' })).then(async (response) => {
      const { payload } = await normalizeResponse(response);
      if (!response.ok || !payload?.success) {
        throw new Error(payload?.error || `Command failed: ${path}`);
      }
      return payload;
    });
  }
}
