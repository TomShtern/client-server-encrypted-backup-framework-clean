export function evaluateConnectionQuality({ latencyMs, successRate }) {
  if (!Number.isFinite(latencyMs)) {
    return 'offline';
  }
  if (latencyMs < 80 && (successRate ?? 1) > 0.95) {
    return 'excellent';
  }
  if (latencyMs < 150 && (successRate ?? 1) > 0.85) {
    return 'good';
  }
  if (latencyMs < 300) {
    return 'fair';
  }
  return 'poor';
}

export function getQualityLabel(quality) {
  switch (quality) {
    case 'excellent':
      return '● Excellent';
    case 'good':
      return '● Good';
    case 'fair':
      return '● Fair';
    case 'poor':
      return '● Poor';
    default:
      return '● Offline';
  }
}
