const DEFAULT_OPTIONS = {
  transports: ['websocket'],
  autoConnect: false,
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 1500,
  reconnectionDelayMax: 8000,
  timeout: 8000,
  withCredentials: true,
};

const DEFAULT_SOCKET_URL =
  typeof globalThis.location === 'object' && globalThis.location
    ? globalThis.location.origin
    : '';

export class SocketClient {
  constructor({ url = DEFAULT_SOCKET_URL, options = {}, onConnect, onDisconnect, onError, onStatus, onProgress, onFileReceipt }) {
    this.url = url ?? DEFAULT_SOCKET_URL;
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.onConnect = typeof onConnect === 'function' ? onConnect : () => {};
    this.onDisconnect = typeof onDisconnect === 'function' ? onDisconnect : () => {};
    this.onError = typeof onError === 'function' ? onError : () => {};
    this.onStatus = typeof onStatus === 'function' ? onStatus : () => {};
    this.onProgress = typeof onProgress === 'function' ? onProgress : () => {};
    this.onFileReceipt = typeof onFileReceipt === 'function' ? onFileReceipt : () => {};

    this.socket = null;
    this.currentJobId = null;
    this.ioFactory = null;
  }

  async start() {
    try {
      const ioFactory = await this.#ensureIoFactory();
      this.socket = ioFactory(this.url, this.options);
    } catch (error) {
      console.warn('Socket initialization failed', error);
      this.onError(error instanceof Error ? error : new Error('Socket initialization failed'));
      return;
    }

    this.socket.on('connect', () => {
      this.onConnect();
      if (this.currentJobId) {
        this.requestStatus(this.currentJobId);
      }
    });

    this.socket.on('disconnect', (reason) => {
      this.onDisconnect(reason);
    });

    this.socket.on('connect_error', (error) => {
      this.onError(error);
    });

    this.socket.on('status', (payload) => {
      this.onStatus(payload);
    });

    this.socket.on('status_response', (payload) => {
      this.onStatus(payload);
    });

    this.socket.on('progress_update', (payload) => {
      if (this.currentJobId && payload?.job_id && payload.job_id !== this.currentJobId) {
        return;
      }
      this.onProgress(payload);
    });

    this.socket.on('file_receipt', (payload) => {
      this.onFileReceipt(payload);
    });

    this.socket.connect();
  }

  stop() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  watchJob(jobId) {
    this.currentJobId = jobId;
    this.requestStatus(jobId);
  }

  clearJob() {
    this.currentJobId = null;
  }

  requestStatus(jobId) {
    if (!this.socket || !jobId) {
      return;
    }
    this.socket.emit('request_status', { job_id: jobId });
  }

  async #ensureIoFactory() {
    if (this.ioFactory) {
      return this.ioFactory;
    }

    if (globalThis.io) {
      this.ioFactory = globalThis.io;
      return this.ioFactory;
    }

    try {
      const module = await import('https://cdn.jsdelivr.net/npm/socket.io-client@4.7.5/dist/socket.io.esm.min.js');
      this.ioFactory = module.io;
      return this.ioFactory;
    } catch (error) {
      throw error instanceof Error ? error : new Error('Unable to load Socket.IO client library');
    }
  }
}
