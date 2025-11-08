import { evaluateConnectionQuality } from './connection-metrics.js';

const DEFAULT_INTERVAL = 7000;

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
    this.timer = window.setInterval(() => this.#tick(), this.interval);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
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
        const metrics = payload?.system_metrics || payload?.systemMetrics || null;
        const backupStatus = payload?.backup_server || payload?.backup_server_status || payload?.backup_server_state;
        const connected = backupStatus === 'running' || payload?.status === 'healthy';
        const quality = evaluateConnectionQuality({ latencyMs: latency, successRate: connected ? 1 : 0 });

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
