import { evaluateConnectionQuality } from './connection-metrics.js';

const DEFAULT_INTERVAL = 7000;

/* CACHE BUSTER v2.0 - Force browser reload */

export class ConnectionMonitor {
  constructor({ api, interval = DEFAULT_INTERVAL, onResult }) {
    this.api = api;
    this.interval = interval;
    this.onResult = typeof onResult === 'function' ? onResult : () => {};
    this.timer = null;
    this.inFlight = null;
  }

  start() {
    this.stop();
    this.#tick();
    this.timer = globalThis.setInterval(() => this.#tick(), this.interval);
  }

  stop() {
    if (this.timer) {
      globalThis.clearInterval(this.timer);
      this.timer = null;
    }
    this.inFlight = null;
  }

  forcePing() {
    this.#tick(true);
  }

  async #tick(force = false) {
    if (this.inFlight && !force) {
      return;
    }

    const started = performance.now();
    const request = this.api
      .health()
      .then((payload) => {
        const latency = performance.now() - started;
        console.log('[ConnectionMonitor] Health check response:', payload);

        const metrics = payload?.system_metrics || payload?.systemMetrics || null;

        // Check multiple possible response formats
        const backupServer = payload?.backup_server || payload?.backup_server_status || payload?.backup_server_state;
        const apiServer = payload?.api_server || payload?.api_server_status;
        const apiStatus = payload?.status;

        // Consider connected if:
        // 1. API server is running (means web API is responding)
        // 2. Backup server is running
        // 3. Overall status is healthy/ok
        const isApiServerRunning = apiServer === 'running' || apiServer === 'active' || apiServer === 'healthy';
        const isBackupRunning = backupServer === 'running' || backupServer === 'active' || backupServer === 'healthy';
        const isHealthy = apiStatus === 'healthy' || apiStatus === 'ok' || apiStatus === 'running';

        const connected = isApiServerRunning || isBackupRunning || isHealthy || Boolean(payload?.success);

        const quality = evaluateConnectionQuality({ latencyMs: latency, successRate: connected ? 1 : 0 });

        console.log('[ConnectionMonitor] Connection status:', {
          connected,
          isApiServerRunning,
          isBackupRunning,
          isHealthy,
          quality,
          latency,
          payload
        });

        this.onResult({
          ok: true,
          latency,
          metrics,
          connected,
          quality,
          timestamp: Date.now(),
        });
      })
      .catch((error) => {
        console.error('[ConnectionMonitor] Health check failed:', error);
        this.onResult({ ok: false, error, timestamp: Date.now() });
      })
      .finally(() => {
        if (this.inFlight === request) {
          this.inFlight = null;
        }
      });

    this.inFlight = request;
    return request;
  }
}
