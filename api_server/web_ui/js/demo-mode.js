/* global safeLocalStorage */

/**
 * Demo Mode Manager
 * Simulates backup transfers for testing and demonstration purposes
 */
class DemoMode {
  #app;
  #enabled;
  #active;
  #timer;
  #totalBytes;

  constructor(app) {
    this.#app = app;
    this.#enabled = this.#detectEnabled();
    this.#active = false;
    this.#timer = null;
    this.#totalBytes = 250 * 1024 * 1024; // 250MB simulated transfer
  }

  get enabled() {
    return this.#enabled;
  }

  get active() {
    return this.#active;
  }

  #detectEnabled() {
    try {
      const params = new URLSearchParams(globalThis.location?.search || '');
      if (params.has('demo')) return true;
      return safeLocalStorage('cyberbackup-demo-mode') === '1';
    } catch {
      return false;
    }
  }

  start() {
    if (!this.#enabled) return;

    // Prevent demo mode from starting during a real backup job
    const currentStatus = this.#app.state.snapshot.status;
    const hasActiveJob = currentStatus === 'uploading' || currentStatus === 'paused';
    const isRealConnection = this.#app.state.snapshot.connected;

    if (hasActiveJob && isRealConnection) {
      this.#app.toast.show('Cannot start demo while real backup is active', 'warn');
      this.#app.logs.add('Demo mode blocked: real backup in progress', { phase: 'DEMO', level: 'warn' });
      return;
    }

    if (this.#active) {
      this.#app.toast.show('Demo already running', 'info');
      return;
    }

    this.#active = true;
    this.#app.logs.add('Demo mode: starting simulated transfer', { phase: 'DEMO', level: 'info' });
    this.#app.setConnectionStatus('Demo mode (simulated) - no network traffic', 'info');

    // Add visual indicator for demo mode
    this.#showDemoBadge();

    this.#app.state.update({
      connected: false,
      jobId: 'demo',
      status: 'uploading',
      progress: 0,
      speed: 0,
      bytesTransferred: 0,
      totalBytes: this.#totalBytes,
      startTime: Date.now(),
    });

    this.#startTimer();
  }

  pause() {
    if (!this.#active) return;
    this.#stopTimer();
    this.#app.state.update({ status: 'paused' });
    this.#app.logs.add('Demo transfer paused', { phase: 'DEMO', level: 'info' });
  }

  resume() {
    if (!this.#active) return;
    this.#app.state.update({ status: 'uploading' });
    this.#app.logs.add('Demo transfer resumed', { phase: 'DEMO', level: 'info' });
    this.#startTimer();
  }

  stop() {
    if (!this.#active) return;
    this.#stopTimer();
    this.#active = false;
    this.#hideDemoBadge();
    this.#app.state.update({
      status: 'idle',
      progress: 0,
      jobId: null,
      speed: 0,
      bytesTransferred: 0
    });
    this.#app.logs.add('Demo transfer stopped', { phase: 'DEMO', level: 'warn' });
    this.#app.toast.show('Demo stopped', 'info');
  }

  #startTimer() {
    if (this.#timer) return;

    this.#timer = setInterval(() => {
      if (!this.#active) {
        this.#stopTimer();
        return;
      }
      if (this.#app.state.snapshot.status !== 'uploading') {
        return;
      }

      const currentPct = Math.max(0, Math.min(100, Number(this.#app.state.snapshot.progress) || 0));
      const bump = 2 + Math.random() * 7;
      const nextPct = Math.min(100, currentPct + bump);
      const totalBytes = this.#app.state.snapshot.totalBytes || 1;

      const speed = 8 * 1024 * 1024 + Math.random() * 3 * 1024 * 1024;
      const bytesTransferred = Math.floor(totalBytes * (nextPct / 100));

      if (nextPct >= 100) {
        this.#app.state.update({
          status: 'completed',
          progress: 100,
          speed: 0,
          bytesTransferred: totalBytes,
        });
        this.#app.logs.add('Demo transfer complete', { phase: 'DEMO', level: 'success' });
        this.#app.toast.show('Demo complete (simulated)', 'success');
        this.#active = false;
        this.#stopTimer();
        this.#hideDemoBadge();
        return;
      }

      this.#app.state.update({
        status: 'uploading',
        progress: nextPct,
        speed,
        bytesTransferred,
      });
    }, 650);
  }

  #stopTimer() {
    if (this.#timer) {
      clearInterval(this.#timer);
      this.#timer = null;
    }
  }

  #showDemoBadge() {
    // Create and show a demo mode badge overlay
    let badge = document.getElementById('demo-mode-badge');
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'demo-mode-badge';
      badge.className = 'demo-mode-badge';
      badge.textContent = 'DEMO MODE';
      badge.setAttribute('aria-label', 'Demo mode active - simulated transfer');
      document.body.appendChild(badge);
    }
    badge.hidden = false;
  }

  #hideDemoBadge() {
    const badge = document.getElementById('demo-mode-badge');
    if (badge) {
      badge.hidden = true;
    }
  }

  destroy() {
    this.#stopTimer();
    this.#active = false;
    this.#hideDemoBadge();
  }
}

// Export to global scope for classic script usage
globalThis.DemoMode = DemoMode;