// Enhanced functionality for Client Web GUI
// Features: validation, file type icons, progress ring states, connection dropdown, log search, speed chart

// File type icon mapping
const FILE_TYPE_ICONS = {
  // Documents
  pdf: { icon: '📄', badge: 'pdf', class: 'pdf' },
  doc: { icon: '📝', badge: 'doc', class: 'doc' },
  docx: { icon: '📝', badge: 'doc', class: 'doc' },
  txt: { icon: '📄', badge: 'txt', class: 'default' },
  rtf: { icon: '📝', badge: 'rtf', class: 'doc' },

  // Spreadsheets
  xls: { icon: '📊', badge: 'xls', class: 'doc' },
  xlsx: { icon: '📊', badge: 'xlsx', class: 'doc' },
  csv: { icon: '📊', badge: 'csv', class: 'doc' },

  // Images
  jpg: { icon: '🖼️', badge: 'jpg', class: 'img' },
  jpeg: { icon: '🖼️', badge: 'jpeg', class: 'img' },
  png: { icon: '🖼️', badge: 'png', class: 'img' },
  gif: { icon: '🖼️', badge: 'gif', class: 'img' },
  svg: { icon: '🖼️', badge: 'svg', class: 'img' },
  webp: { icon: '🖼️', badge: 'webp', class: 'img' },

  // Videos
  mp4: { icon: '🎥', badge: 'mp4', class: 'video' },
  avi: { icon: '🎥', badge: 'avi', class: 'video' },
  mkv: { icon: '🎥', badge: 'mkv', class: 'video' },
  mov: { icon: '🎥', badge: 'mov', class: 'video' },

  // Audio
  mp3: { icon: '🎵', badge: 'mp3', class: 'audio' },
  wav: { icon: '🎵', badge: 'wav', class: 'audio' },
  flac: { icon: '🎵', badge: 'flac', class: 'audio' },

  // Archives
  zip: { icon: '📦', badge: 'zip', class: 'archive' },
  rar: { icon: '📦', badge: 'rar', class: 'archive' },
  '7z': { icon: '📦', badge: '7z', class: 'archive' },
  tar: { icon: '📦', badge: 'tar', class: 'archive' },
  gz: { icon: '📦', badge: 'gz', class: 'archive' },

  // Code
  js: { icon: '💻', badge: 'js', class: 'code' },
  py: { icon: '💻', badge: 'py', class: 'code' },
  html: { icon: '💻', badge: 'html', class: 'code' },
  css: { icon: '💻', badge: 'css', class: 'code' },
  json: { icon: '💻', badge: 'json', class: 'code' },
  xml: { icon: '💻', badge: 'xml', class: 'code' },

  // Default
  default: { icon: '📄', badge: 'file', class: 'default' }
};

// Get file type info
function getFileTypeInfo(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  return FILE_TYPE_ICONS[ext] || FILE_TYPE_ICONS.default;
}

// Format file modified date
function formatModifiedDate(date) {
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    return 'Today';
  } else if (days === 1) {
    return 'Yesterday';
  } else if (days < 7) {
    return `${days} days ago`;
  } else {
    return date.toLocaleDateString();
  }
}

// Update file card with rich preview
function updateFileCardPreview(file) {
  if (!file) return;

  const fileIcon = document.getElementById('fileIcon');
  const fileName = document.getElementById('fileName');
  const fileInfo = document.getElementById('fileInfo');
  const fileMetadata = document.getElementById('fileMetadata');
  const fileTypeBadge = document.getElementById('fileTypeBadge');
  const fileModified = document.getElementById('fileModified');

  const typeInfo = getFileTypeInfo(file.name);
  const sizeFormatted = formatBytes(file.size);
  const modifiedDate = formatModifiedDate(new Date(file.lastModified));

  // Update icon
  if (fileIcon) {
    fileIcon.textContent = typeInfo.icon;
  }

  // Update file name
  if (fileName) {
    fileName.textContent = file.name;
  }

  // Update file info
  if (fileInfo) {
    fileInfo.textContent = `${sizeFormatted} • ${file.type || 'Unknown type'}`;
  }

  // Update metadata
  if (fileMetadata) {
    fileMetadata.style.display = 'flex';
  }

  if (fileTypeBadge) {
    fileTypeBadge.textContent = typeInfo.badge.toUpperCase();
    fileTypeBadge.className = `file-badge ${typeInfo.class}`;
  }

  if (fileModified) {
    fileModified.textContent = `Modified: ${modifiedDate}`;
  }
}

// Helper function for file size formatting (if not already available)
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Progress ring state manager
const ProgressRingStates = {
  IDLE: 'idle',
  CONNECTING: 'connecting',
  ACTIVE: 'active',
  PAUSED: 'paused',
  COMPLETE: 'complete',
  ERROR: 'error'
};

function updateProgressRingState(state) {
  const ring = document.getElementById('progressRing');
  if (!ring) return;

  // Remove all state classes
  Object.values(ProgressRingStates).forEach(s => ring.classList.remove(s));

  // Add new state
  ring.classList.add(state);
}

// Input validation
function validateServerInput(value) {
  // Regex for IP:PORT format
  const regex = /^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$/;
  return regex.test(value);
}

function validateUsername(value) {
  // Alphanumeric, 3-20 characters
  const regex = /^[a-zA-Z0-9_]{3,20}$/;
  return regex.test(value);
}

function updateValidationIcon(inputId, iconId, isValid) {
  const icon = document.getElementById(iconId);
  if (!icon) return;

  if (isValid === null) {
    icon.className = 'validation-icon hidden';
    icon.textContent = '';
  } else if (isValid) {
    icon.className = 'validation-icon valid';
    icon.textContent = '✓';
  } else {
    icon.className = 'validation-icon invalid';
    icon.textContent = '✕';
  }
}

// Setup validation listeners
function setupValidation() {
  const serverInput = document.getElementById('serverInput');
  const usernameInput = document.getElementById('usernameInput');

  if (serverInput) {
    serverInput.addEventListener('blur', () => {
      const isValid = validateServerInput(serverInput.value);
      updateValidationIcon('serverInput', 'serverValidIcon', isValid);
      const hint = document.getElementById('serverHint');
      if (hint) {
        hint.hidden = isValid;
      }
      serverInput.setAttribute('aria-invalid', !isValid);
      updatePrimaryButtonState();
    });

    serverInput.addEventListener('input', () => {
      updateValidationIcon('serverInput', 'serverValidIcon', null);
      const hint = document.getElementById('serverHint');
      if (hint) hint.hidden = true;
    });
  }

  if (usernameInput) {
    usernameInput.addEventListener('blur', () => {
      const isValid = validateUsername(usernameInput.value);
      updateValidationIcon('usernameInput', 'usernameValidIcon', isValid);
      const hint = document.getElementById('usernameHint');
      if (hint) {
        hint.hidden = isValid;
      }
      usernameInput.setAttribute('aria-invalid', !isValid);
      updatePrimaryButtonState();
    });

    usernameInput.addEventListener('input', () => {
      updateValidationIcon('usernameInput', 'usernameValidIcon', null);
      const hint = document.getElementById('usernameHint');
      if (hint) hint.hidden = true;
    });
  }
}

// Primary button state manager
function updatePrimaryButtonState() {
  const btn = document.getElementById('primaryActionBtn');
  const btnText = document.getElementById('primaryBtnText');
  const fileInput = document.getElementById('fileInput');
  const serverInput = document.getElementById('serverInput');
  const usernameInput = document.getElementById('usernameInput');

  if (!btn || !btnText) return;

  const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
  const serverValid = serverInput && validateServerInput(serverInput.value);
  const usernameValid = usernameInput && validateUsername(usernameInput.value);

  // Check connection state from app
  const isConnected = globalThis.cyberBackupApp?.state?.isConnected || false;
  const isTransferring = globalThis.cyberBackupApp?.state?.isTransferring || false;

  if (isTransferring) {
    btnText.textContent = 'Transferring...';
    btn.disabled = true;
  } else if (!hasFile) {
    btnText.textContent = 'Select a file first';
    btn.disabled = true;
  } else if (!serverValid || !usernameValid) {
    btnText.textContent = 'Check inputs';
    btn.disabled = true;
  } else if (isConnected) {
    btnText.textContent = '🚀 Start Backup';
    btn.disabled = false;
  } else {
    btnText.textContent = '🔌 Connect to Server';
    btn.disabled = false;
  }
}

// Connection dropdown toggle
function setupConnectionDropdown() {
  const statusBadge = document.getElementById('connStatus');
  const dropdown = document.getElementById('connectionDetails');

  if (!statusBadge || !dropdown) return;

  statusBadge.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && !statusBadge.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });
}

// Log search functionality
function setupLogSearch() {
  const searchInput = document.getElementById('logSearchInput');
  const logContainer = document.getElementById('logContainer');

  if (!searchInput || !logContainer) return;

  let searchTimeout;

  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const query = searchInput.value.toLowerCase().trim();
      filterLogs(query);
    }, 300); // Debounce 300ms
  });
}

function filterLogs(query) {
  const logContainer = document.getElementById('logContainer');
  if (!logContainer) return;

  const logEntries = logContainer.querySelectorAll('[data-log-entry]');

  if (!query) {
    logEntries.forEach(entry => {
      entry.style.display = '';
    });
    return;
  }

  logEntries.forEach(entry => {
    const text = entry.textContent.toLowerCase();
    if (text.includes(query)) {
      entry.style.display = '';
    } else {
      entry.style.display = 'none';
    }
  });
}

// Speed chart implementation
class SpeedChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.dataPoints = [];
    this.maxDataPoints = 30; // 30 seconds of data
    this.maxSpeed = 0;

    // Setup canvas size
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.draw();
  }

  addDataPoint(speed) {
    this.dataPoints.push(speed);

    // Keep only last N points
    if (this.dataPoints.length > this.maxDataPoints) {
      this.dataPoints.shift();
    }

    // Update max for scaling
    this.maxSpeed = Math.max(...this.dataPoints, this.maxSpeed * 0.95);

    this.draw();
  }

  draw() {
    if (!this.ctx || this.dataPoints.length === 0) return;

    const width = this.canvas.width / window.devicePixelRatio;
    const height = this.canvas.height / window.devicePixelRatio;
    const padding = 10;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw grid lines
    this.ctx.strokeStyle = '#30363d';
    this.ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padding, y);
      this.ctx.lineTo(width - padding, y);
      this.ctx.stroke();
    }

    // Draw line chart
    this.ctx.strokeStyle = '#58a6ff';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    this.dataPoints.forEach((speed, index) => {
      const x = padding + (chartWidth / (this.maxDataPoints - 1)) * index;
      const y = padding + chartHeight - (speed / this.maxSpeed) * chartHeight;

      if (index === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });

    this.ctx.stroke();

    // Draw fill gradient
    this.ctx.lineTo(width - padding, height - padding);
    this.ctx.lineTo(padding, height - padding);
    this.ctx.closePath();

    const gradient = this.ctx.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, 'rgba(88, 166, 255, 0.2)');
    gradient.addColorStop(1, 'rgba(88, 166, 255, 0.0)');
    this.ctx.fillStyle = gradient;
    this.ctx.fill();
  }

  clear() {
    this.dataPoints = [];
    this.maxSpeed = 0;
    if (this.ctx) {
      const width = this.canvas.width / window.devicePixelRatio;
      const height = this.canvas.height / window.devicePixelRatio;
      this.ctx.clearRect(0, 0, width, height);
    }
  }
}

// Initialize speed chart
let speedChart;

function setupSpeedChart() {
  speedChart = new SpeedChart('speedChart');

  const toggleBtn = document.getElementById('toggleSpeedChart');
  const container = document.getElementById('speedChartContainer');

  if (toggleBtn && container) {
    toggleBtn.addEventListener('click', () => {
      const isVisible = container.classList.contains('show');
      if (isVisible) {
        container.classList.remove('show');
        toggleBtn.textContent = 'Show Chart';
      } else {
        container.classList.add('show');
        toggleBtn.textContent = 'Hide Chart';
        if (speedChart) speedChart.draw();
      }
    });
  }
}

// Theme toggle with smooth transition
function setupThemeToggle() {
  const themeBtn = document.getElementById('themeToggle');
  if (!themeBtn) return;

  themeBtn.addEventListener('click', () => {
    // Add rotating animation
    themeBtn.classList.add('rotating');
    setTimeout(() => themeBtn.classList.remove('rotating'), 600);

    // Toggle theme (this part should integrate with existing theme manager)
    const html = document.documentElement;
    const isDark = html.classList.contains('theme-dark');

    if (isDark) {
      html.classList.remove('theme-dark');
      html.classList.add('theme-light');
      themeBtn.textContent = '🌙 Dark mode';
    } else {
      html.classList.add('theme-dark');
      html.classList.remove('theme-light');
      themeBtn.textContent = '☀️ Light mode';
    }
  });
}

// Data particles initialization (safe DOM methods)
function initDataParticles() {
  const container = document.getElementById('dataParticles');
  if (!container) return;

  // Clear any existing particles safely
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }

  // Create particles based on screen size (reduced for performance)
  const particleCount = window.innerWidth > 1200 ? 8 : window.innerWidth > 768 ? 5 : 3;

  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // Randomize particle position and animation
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (12 + Math.random() * 10) + 's';

    container.appendChild(particle);
  }
}

// Ripple effect handler
function initRippleEffects() {
  document.addEventListener('click', (e) => {
    const target = e.target.closest('.ripple');
    if (!target) return;

    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';

    target.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
}

// Floating label enhancement
function initFloatingLabels() {
  const floatingLabels = document.querySelectorAll('.floating-label input');

  floatingLabels.forEach(input => {
    // Check if input has value on load
    const checkValue = () => {
      if (input.value) {
        input.classList.add('has-value');
      } else {
        input.classList.remove('has-value');
      }
    };

    checkValue();

    input.addEventListener('focus', () => {
      input.classList.add('focused');
    });

    input.addEventListener('blur', () => {
      input.classList.remove('focused');
      checkValue();
    });

    input.addEventListener('input', checkValue);
  });
}

// Initialize all enhancements
function initializeEnhancements() {
  setupValidation();
  setupConnectionDropdown();
  setupLogSearch();
  setupSpeedChart();
  setupThemeToggle();

  // Enhanced interactions
  initDataParticles();
  initRippleEffects();
  initFloatingLabels();

  // Set initial progress ring state
  updateProgressRingState(ProgressRingStates.IDLE);

  // Set initial button state
  updatePrimaryButtonState();

  // Watch for file selection changes
  const fileInput = document.getElementById('fileInput');
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        updateFileCardPreview(fileInput.files[0]);
      }
      updatePrimaryButtonState();
    });
  }

  // Responsive particle count on resize
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      initDataParticles();
    }, 250);
  });
}

// Export functions for use by main app
if (typeof window !== 'undefined') {
  window.Enhancements = {
    updateProgressRingState,
    updatePrimaryButtonState,
    updateFileCardPreview,
    getFileTypeInfo,
    speedChart: () => speedChart,
    ProgressRingStates,
    initializeEnhancements
  };
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeEnhancements);
} else {
  initializeEnhancements();
}

export {
  updateProgressRingState,
  updatePrimaryButtonState,
  updateFileCardPreview,
  getFileTypeInfo,
  ProgressRingStates,
  initializeEnhancements,
  speedChart,
  initDataParticles,
  initRippleEffects,
  initFloatingLabels
};
