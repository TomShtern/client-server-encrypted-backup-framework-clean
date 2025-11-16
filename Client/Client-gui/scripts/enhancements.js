/**
 * Professional Desktop Web GUI Enhancements
 * JavaScript enhancements for improved user experience
 */

class ProfessionalGUIEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupSidebarEnhancements();
        this.setupProgressEnhancements();
        this.setupButtonHierarchy();
        this.setupBrowserBehavior();
        this.setupAccessibility();
        this.setupProfessionalInteractions();
    }

    // Instance method: Setup sidebar-specific interactions
    setupSidebarEnhancements() {
        try {
            const sidebar = document.querySelector('aside.stack');
            if (!sidebar) return;

            // Allow collapsing/expanding the sidebar by clicking the header area
            const title = sidebar.querySelector('.phase');
            if (title) {
                title.style.cursor = 'pointer';
                title.addEventListener('click', () => {
                    sidebar.classList.toggle('collapsed');
                });
            }

            // Add hover depth class using CSS already present
            sidebar.addEventListener('mouseenter', () => sidebar.classList.add('hovered'));
            sidebar.addEventListener('mouseleave', () => sidebar.classList.remove('hovered'));
        } catch (e) {
            console.warn('setupSidebarEnhancements failed', e);
        }
    }

    // Instance method: Setup progress ring behaviors and smoothing
    setupProgressEnhancements() {
        try {
            const ring = document.getElementById('progressRing');
            const progressArc = document.getElementById('progressArc');
            const pct = document.getElementById('progressPct');
            if (!ring || !progressArc || !pct) return;

            // Expose helper that adjusts arc and text smoothly
            const update = (value = 0) => {
                const max = 282.743; // circumference approximation used in markup
                const clamped = Math.max(0, Math.min(100, value));
                const offset = max - (clamped / 100) * max;
                progressArc.style.strokeDashoffset = offset;
                pct.textContent = `${Math.round(clamped)}%`;
            };

            // Defensive: store as property for other features
            this._updateProgress = update;

            // Hovering shows a glow; clicking toggles a small demo animation
            ring.addEventListener('click', () => {
                ProfessionalGUIEnhancements.updateProgressRingState(ProfessionalGUIEnhancements.ProgressRingStates.ACTIVE);
                // animate 0 -> 100 -> 0 fast for dev/demo
                let v = 0;
                const t = setInterval(() => {
                    v += 10;
                    update(v);
                    if (v >= 100) {
                        clearInterval(t);
                        setTimeout(() => update(0), 400);
                    }
                }, 60);
            });
        } catch (e) {
            console.warn('setupProgressEnhancements failed', e);
        }
    }

    // Instance method: Setup button behaviors and state wiring
    setupButtonHierarchy() {
        try {
            // Primary button wiring
            const primary = document.getElementById('primaryActionBtn');
            const fileInput = document.getElementById('fileInput');
            const fileSelectBtn = document.getElementById('fileSelectBtn');
            const clearBtn = document.getElementById('clearFileBtn');

            if (fileSelectBtn && fileInput) {
                fileSelectBtn.addEventListener('click', () => fileInput.click());
            }

            if (clearBtn && fileInput) {
                clearBtn.addEventListener('click', () => {
                    fileInput.value = null;
                    const fileName = document.getElementById('fileName');
                    if (fileName) fileName.textContent = 'Drag & drop a file here or choose above';
                    ProfessionalGUIEnhancements.updatePrimaryButtonState();
                });
            }

            // Primary action: if not connected, attempt to toggle a simulated connection; if connected, start demo transfer
            if (primary) {
                primary.addEventListener('click', () => {
                    const isConnected = globalThis.cyberBackupApp?.state?.isConnected || false;
                    if (!isConnected) {
                        // Simulate connecting if app is not present
                        if (!globalThis.cyberBackupApp) globalThis.cyberBackupApp = { state: { isConnected: true, isTransferring: false } };
                        else globalThis.cyberBackupApp.state.isConnected = true;
                        ProfessionalGUIEnhancements.updatePrimaryButtonState();
                        // close status detail dropdown for clarity
                        const dropdown = document.getElementById('connectionDetails');
                        if (dropdown) dropdown.classList.remove('show');
                    } else {
                        // Simulate transfer
                        if (!globalThis.cyberBackupApp.state.isTransferring) {
                            globalThis.cyberBackupApp.state.isTransferring = true;
                            ProfessionalGUIEnhancements.updatePrimaryButtonState();
                            if (this._updateProgress) {
                                let v = 0;
                                const t = setInterval(() => { v += 5; this._updateProgress(v); if (v >= 100) { clearInterval(t); globalThis.cyberBackupApp.state.isTransferring = false; ProfessionalGUIEnhancements.updatePrimaryButtonState(); } }, 250);
                            }
                        }
                    }
                });
            }
        } catch (e) {
            console.warn('setupButtonHierarchy failed', e);
        }
    }

    // Instance method: Misc browser behavior such as preventing accidental navigations and drag/drop
    setupBrowserBehavior() {
        try {
            // Prevent file drag from navigating away
            window.addEventListener('dragover', (e) => e.preventDefault());
            window.addEventListener('drop', (e) => e.preventDefault());

            // Allow drop zone to accept files
            const dropZone = document.getElementById('fileDropZone');
            const fileInput = document.getElementById('fileInput');
            const fileName = document.getElementById('fileName');
            const fileInfo = document.getElementById('fileInfo');

            if (dropZone && fileInput) {
                dropZone.addEventListener('dragenter', () => dropZone.classList.add('drag-over'));
                dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
                dropZone.addEventListener('drop', (e) => {
                    dropZone.classList.remove('drag-over');
                    const files = e.dataTransfer?.files;
                    if (files && files.length > 0) {
                        fileInput.files = files;
                        if (fileName) fileName.textContent = files[0].name;
                        if (fileInfo) fileInfo.textContent = `${ProfessionalGUIEnhancements.formatBytes(files[0].size)} • ${files[0].type || 'Unknown'}`;
                        ProfessionalGUIEnhancements.updatePrimaryButtonState();
                    }
                });
            }
        } catch (e) {
            console.warn('setupBrowserBehavior failed', e);
        }
    }

    // Instance method: improve keyboard and screen reader accessibility
    setupAccessibility() {
        try {
            // Ensure keyboard focus flows to primary button
            const primary = document.getElementById('primaryActionBtn');
            if (primary) {
                primary.setAttribute('aria-pressed', 'false');
                primary.addEventListener('click', () => primary.setAttribute('aria-pressed', String(primary.getAttribute('aria-pressed') === 'false')));
            }

            // Add focus outlines for keyboard users on interactive elements
            document.querySelectorAll('.interactive').forEach(el => {
                el.setAttribute('tabindex', '0');
            });
        } catch (e) {
            console.warn('setupAccessibility failed', e);
        }
    }

    // Instance method: Professional interactions like log filter buttons and pause/resume / stop simulator
    setupProfessionalInteractions() {
        try {
            // Wire log filter controls
            const filterButtons = document.querySelectorAll('.filter-btn');
            if (filterButtons && filterButtons.length) {
                filterButtons.forEach(btn => {
                    btn.addEventListener('click', () => {
                        filterButtons.forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        // For local mode, just set aria-pressed
                        btn.setAttribute('aria-pressed', 'true');
                    });
                });
            }

            // Pause/resume/stop simulation buttons
            const pauseBtn = document.getElementById('pauseBtn');
            const resumeBtn = document.getElementById('resumeBtn');
            const stopBtn = document.getElementById('stopBtn');
            if (pauseBtn) pauseBtn.addEventListener('click', () => { if (globalThis.cyberBackupApp) globalThis.cyberBackupApp.state.isTransferring = false; ProfessionalGUIEnhancements.updatePrimaryButtonState(); });
            if (resumeBtn) resumeBtn.addEventListener('click', () => { if (globalThis.cyberBackupApp) globalThis.cyberBackupApp.state.isTransferring = true; ProfessionalGUIEnhancements.updatePrimaryButtonState(); });
            if (stopBtn) stopBtn.addEventListener('click', () => { if (globalThis.cyberBackupApp) { globalThis.cyberBackupApp.state.isTransferring = false; globalThis.cyberBackupApp.state.isConnected = false; } ProfessionalGUIEnhancements.updatePrimaryButtonState(); });
        } catch (e) {
            console.warn('setupProfessionalInteractions failed', e);
        }
    }

    // File type icon mapping
    static FILE_TYPE_ICONS = {
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
    static getFileTypeInfo(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        return ProfessionalGUIEnhancements.FILE_TYPE_ICONS[ext] || ProfessionalGUIEnhancements.FILE_TYPE_ICONS.default;
    }

    // Format file modified date
    static formatModifiedDate(date) {
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
    static updateFileCardPreview(file) {
        if (!file) return;

        const fileIcon = document.getElementById('fileIcon');
        const fileName = document.getElementById('fileName');
        const fileInfo = document.getElementById('fileInfo');
        const fileMetadata = document.getElementById('fileMetadata');
        const fileTypeBadge = document.getElementById('fileTypeBadge');
        const fileModified = document.getElementById('fileModified');

        const typeInfo = ProfessionalGUIEnhancements.getFileTypeInfo(file.name);
        const sizeFormatted = ProfessionalGUIEnhancements.formatBytes(file.size);
        const modifiedDate = ProfessionalGUIEnhancements.formatModifiedDate(new Date(file.lastModified));

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

    // Helper function for file size formatting
    static formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Progress ring state manager
    static ProgressRingStates = {
        IDLE: 'idle',
        CONNECTING: 'connecting',
        ACTIVE: 'active',
        PAUSED: 'paused',
        COMPLETE: 'complete',
        ERROR: 'error'
    };

    static updateProgressRingState(state) {
        const ring = document.getElementById('progressRing');
        if (!ring) return;

        // Remove all state classes
        Object.values(ProfessionalGUIEnhancements.ProgressRingStates).forEach(s => ring.classList.remove(s));

        // Add new state
        ring.classList.add(state);
    }

    // Input validation
    static validateServerInput(value) {
        // Regex for IP:PORT format
        const regex = /^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$/;
        return regex.test(value);
    }

    static validateUsername(value) {
        // Alphanumeric, 3-20 characters
        const regex = /^[a-zA-Z0-9_]{3,20}$/;
        return regex.test(value);
    }

    static updateValidationIcon(inputId, iconId, isValid) {
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
    static setupValidation() {
        const serverInput = document.getElementById('serverInput');
        const usernameInput = document.getElementById('usernameInput');

        if (serverInput) {
            serverInput.addEventListener('blur', () => {
                const isValid = ProfessionalGUIEnhancements.validateServerInput(serverInput.value);
                ProfessionalGUIEnhancements.updateValidationIcon('serverInput', 'serverValidIcon', isValid);
                const hint = document.getElementById('serverHint');
                if (hint) {
                    hint.hidden = isValid;
                }
                serverInput.setAttribute('aria-invalid', !isValid);
                ProfessionalGUIEnhancements.updatePrimaryButtonState();
            });

            serverInput.addEventListener('input', () => {
                ProfessionalGUIEnhancements.updateValidationIcon('serverInput', 'serverValidIcon', null);
                const hint = document.getElementById('serverHint');
                if (hint) hint.hidden = true;
            });
        }

        if (usernameInput) {
            usernameInput.addEventListener('blur', () => {
                const isValid = ProfessionalGUIEnhancements.validateUsername(usernameInput.value);
                ProfessionalGUIEnhancements.updateValidationIcon('usernameInput', 'usernameValidIcon', isValid);
                const hint = document.getElementById('usernameHint');
                if (hint) {
                    hint.hidden = isValid;
                }
                usernameInput.setAttribute('aria-invalid', !isValid);
                ProfessionalGUIEnhancements.updatePrimaryButtonState();
            });

            usernameInput.addEventListener('input', () => {
                ProfessionalGUIEnhancements.updateValidationIcon('usernameInput', 'usernameValidIcon', null);
                const hint = document.getElementById('usernameHint');
                if (hint) hint.hidden = true;
            });
        }
    }

// Primary button state manager
    static updatePrimaryButtonState() {
        const btn = document.getElementById('primaryActionBtn');
        const btnText = document.getElementById('primaryBtnText');
        const fileInput = document.getElementById('fileInput');
        const serverInput = document.getElementById('serverInput');
        const usernameInput = document.getElementById('usernameInput');

        if (!btn || !btnText) return;

        const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
        const serverValid = serverInput && ProfessionalGUIEnhancements.validateServerInput(serverInput.value);
        const usernameValid = usernameInput && ProfessionalGUIEnhancements.validateUsername(usernameInput.value);

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
    static setupConnectionDropdown() {
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
    static setupLogSearch() {
        const searchInput = document.getElementById('logSearchInput');
        const logContainer = document.getElementById('logContainer');

        if (!searchInput || !logContainer) return;

        let searchTimeout;

        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = searchInput.value.toLowerCase().trim();
                ProfessionalGUIEnhancements.filterLogs(query);
            }, 300); // Debounce 300ms
        });
    }

    static filterLogs(query) {
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

    // Speed chart implementation (inner class)
    static SpeedChart = class {
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
    static setupSpeedChart() {
        const speedChart = new ProfessionalGUIEnhancements.SpeedChart('speedChart');

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
    static setupThemeToggle() {
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
    static initDataParticles() {
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
    static initRippleEffects() {
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
    static initFloatingLabels() {
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
    static initializeEnhancements() {
        ProfessionalGUIEnhancements.addEnhancementStyles();
        ProfessionalGUIEnhancements.setupValidation();
        ProfessionalGUIEnhancements.setupConnectionDropdown();
        ProfessionalGUIEnhancements.setupLogSearch();
        ProfessionalGUIEnhancements.setupSpeedChart();
        ProfessionalGUIEnhancements.setupThemeToggle();

        // Enhanced interactions
        ProfessionalGUIEnhancements.initDataParticles();
        ProfessionalGUIEnhancements.initRippleEffects();
        ProfessionalGUIEnhancements.initFloatingLabels();

        // Set initial progress ring state
        ProfessionalGUIEnhancements.updateProgressRingState(ProfessionalGUIEnhancements.ProgressRingStates.IDLE);

        // Set initial button state
        ProfessionalGUIEnhancements.updatePrimaryButtonState();

        // Watch for file selection changes
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', () => {
                if (fileInput.files && fileInput.files[0]) {
                    ProfessionalGUIEnhancements.updateFileCardPreview(fileInput.files[0]);
                }
                ProfessionalGUIEnhancements.updatePrimaryButtonState();
            });
        }

        // Responsive particle count on resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                ProfessionalGUIEnhancements.initDataParticles();
            }, 250);
        });

        // Initialize new professional enhancements
        new ProfessionalGUIEnhancements();
    }

    // Add CSS animations for enhancement effects
    static addEnhancementStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }

            .success-pulse {
                animation: successPulse 1s ease-out;
            }

            @keyframes successPulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }

            .label-focused {
                transform: translateY(-1px);
            }

            .input-valid {
                border-color: var(--success) !important;
            }

            .input-invalid {
                border-color: var(--danger) !important;
            }

            .primary-hover {
                transform: translateY(-2px) !important;
            }

            .secondary-hover {
                transform: translateY(-1px) !important;
            }

            .card-hover {
                transform: translateY(-2px) !important;
            }

            .badge-hover {
                transform: scale(1.05) !important;
            }

            .element-focused {
                outline: 2px solid var(--focus) !important;
                outline-offset: 2px !important;
            }

            .tab-inactive {
                opacity: 0.8;
            }

            .refreshing {
                animation: refreshing 1s ease-in-out;
            }

            @keyframes refreshing {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .resizing {
                transition: all 0.3s ease !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Export for potential external use
window.ProfessionalGUIEnhancements = ProfessionalGUIEnhancements;

// Export functions for use by main app
if (typeof window !== 'undefined') {
    window.Enhancements = {
        updateProgressRingState: ProfessionalGUIEnhancements.updateProgressRingState,
        updatePrimaryButtonState: ProfessionalGUIEnhancements.updatePrimaryButtonState,
        updateFileCardPreview: ProfessionalGUIEnhancements.updateFileCardPreview,
        getFileTypeInfo: ProfessionalGUIEnhancements.getFileTypeInfo,
        speedChart: () => ProfessionalGUIEnhancements.speedChart,
        ProgressRingStates: ProfessionalGUIEnhancements.ProgressRingStates,
        initializeEnhancements: ProfessionalGUIEnhancements.initializeEnhancements
    };
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ProfessionalGUIEnhancements.initializeEnhancements);
} else {
    ProfessionalGUIEnhancements.initializeEnhancements();
}

export {
    ProfessionalGUIEnhancements,
    ProfessionalGUIEnhancements as default
};