export class ScreenReaderAnnouncer {
  constructor(liveRegion) {
    this.liveRegion = liveRegion;
    this._pendingMessages = [];
    this._isAnnouncing = false;
  }

  announce(message) {
    if (!this.liveRegion) return;
    this._pendingMessages.push(String(message));
    if (!this._isAnnouncing) {
      void this.#flushQueue();
    }
  }

  async #flushQueue() {
    this._isAnnouncing = true;
    while (this._pendingMessages.length > 0) {
      const next = this._pendingMessages.shift();
      if (!next) {
        continue;
      }
      this.liveRegion.textContent = '';
      await new Promise((resolve) => {
        requestAnimationFrame(() => {
          this.liveRegion.textContent = next;
          setTimeout(resolve, 120);
        });
      });
    }
    this._isAnnouncing = false;
  }
}
