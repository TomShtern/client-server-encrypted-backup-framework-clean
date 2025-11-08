const BYTE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'];

export function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) {
    return '—';
  }
  if (bytes === 0) {
    return '0 B';
  }
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), BYTE_UNITS.length - 1);
  const value = bytes / Math.pow(1024, exponent);

  let precision;
  if (value >= 100) {
    precision = 0;
  } else if (value >= 10) {
    precision = 1;
  } else {
    precision = 2;
  }

  return `${value.toFixed(precision)} ${BYTE_UNITS[exponent]}`;
}

export function formatSpeed(bytesPerSecond) {
  if (!Number.isFinite(bytesPerSecond) || bytesPerSecond < 0) {
    return '—';
  }
  if (bytesPerSecond === 0) {
    return '0 B/s';
  }
  const exponent = Math.min(Math.floor(Math.log(bytesPerSecond) / Math.log(1024)), BYTE_UNITS.length - 1);
  const value = bytesPerSecond / Math.pow(1024, exponent);

  let precision;
  if (value >= 100) {
    precision = 0;
  } else if (value >= 10) {
    precision = 1;
  } else {
    precision = 2;
  }

  return `${value.toFixed(precision)} ${BYTE_UNITS[exponent]}/s`;
}

export function formatDuration(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return '—';
  }
  if (seconds < 1) {
    return `${seconds.toFixed(1)} s`;
  }
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs}h ${mins.toString().padStart(2, '0')}m`;
  }
  if (mins > 0) {
    return `${mins}m ${secs.toString().padStart(2, '0')}s`;
  }
  return `${secs}s`;
}

export function formatLatency(ms) {
  if (!Number.isFinite(ms) || ms <= 0) {
    return '—';
  }
  return `${Math.max(1, Math.round(ms))} ms`;
}

export function formatPercentage(value) {
  if (!Number.isFinite(value)) {
    return '0%';
  }
  return `${Math.min(100, Math.max(0, value)).toFixed(0)}%`;
}

export function parseServerAddress(input) {
  if (!input || typeof input !== 'string') {
    return null;
  }
  const trimmed = input.trim();
  if (trimmed.length === 0) {
    return null;
  }

  const hasColon = trimmed.includes(':');
  if (!hasColon) {
    return { host: trimmed, port: 1256 };
  }

  const [hostPart, portPart] = trimmed.split(':');
  const parsedPort = Number.parseInt(portPart, 10);
  if (!Number.isFinite(parsedPort) || parsedPort <= 0 || parsedPort > 65535) {
    return null;
  }
  return { host: hostPart, port: parsedPort };
}
