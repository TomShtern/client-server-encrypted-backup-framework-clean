function getElement(id) {
  const el = document.getElementById(id);
  if (!el) {
    throw new Error(`Missing required element: #${id}`);
  }
  return el;
}

export function querySelector(selector, parent = document) {
  const el = parent.querySelector(selector);
  if (!el) {
    throw new Error(`Missing required element for selector: ${selector}`);
  }
  return el;
}

export const dom = {
  container: querySelector('.container'),
  statusOutput: getElement('statusOutput'),
  connStatus: getElement('connStatus'),
  connHealth: getElement('connHealth'),
  connQuality: getElement('connQuality'),
  themeToggle: getElement('themeToggle'),
  serverInput: getElement('serverInput'),
  usernameInput: getElement('usernameInput'),
  serverHint: getElement('serverHint'),
  usernameHint: getElement('usernameHint'),
  fileDropZone: getElement('fileDropZone'),
  fileSelectBtn: getElement('fileSelectBtn'),
  fileInput: getElement('fileInput'),
  recentFilesBtn: getElement('recentFilesBtn'),
  clearFileBtn: getElement('clearFileBtn'),
  fileName: getElement('fileName'),
  fileInfo: getElement('fileInfo'),
  primaryActionBtn: getElement('primaryActionBtn'),
  pauseBtn: getElement('pauseBtn'),
  resumeBtn: getElement('resumeBtn'),
  stopBtn: getElement('stopBtn'),
  advChunkSize: getElement('advChunkSize'),
  advRetryLimit: getElement('advRetryLimit'),
  advResetBtn: getElement('advResetBtn'),
  phaseText: getElement('phaseText'),
  progressArc: getElement('progressArc'),
  progressPct: getElement('progressPct'),
  etaText: getElement('etaText'),
  stats: {
    bytes: getElement('statBytes'),
    speed: getElement('statSpeed'),
    size: getElement('statSize'),
    elapsed: getElement('statElapsed'),
  },
  logFilters: [
    getElement('filterAll'),
    getElement('filterInfo'),
    getElement('filterWarn'),
    getElement('filterError'),
  ],
  logAutoscrollToggle: getElement('logAutoscrollToggle'),
  logExportBtn: getElement('logExportBtn'),
  logContainer: getElement('logContainer'),
  toastStack: getElement('toastStack'),
  modal: getElement('modalConfirm'),
  modalCancelBtn: getElement('modalCancelBtn'),
  modalOkBtn: getElement('modalOkBtn'),
  srLive: getElement('srLive'),
};
