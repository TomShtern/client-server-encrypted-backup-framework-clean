/**
 * CyberBackup Client - UI Core
 * Theme management, Visualizations, and Global GUI Enhancements.
 * Depends on: config.js, core-utils.js
 */
/* global dom, getStorageWithFallback, setStorageWithFallback, domUtils, formatters, LogInspector, SparklineChart */

// --- Theme Management ---

class ThemeManager {
    constructor(themeToggle, themeLabel) {
        this.themeToggle = themeToggle || dom.themeToggle;
        this.themeModeButton = themeLabel || dom.themeLabel;
        this.prefersDark = globalThis.matchMedia('(prefers-color-scheme: dark)');

        // Support theme modes: 'dark', 'light', 'auto'
        const saved = getStorageWithFallback('theme');
        const allowed = new Set(['dark', 'light', 'auto']);
        this.mode = allowed.has(saved) ? saved : 'auto';
        this.currentTheme = this.#resolveTheme();

        // Phase 2: Performance mode
        this.performanceMode = getStorageWithFallback('performanceMode') === 'true';
        this.#init();
    }

    #resolveTheme() {
        if (this.mode === 'auto') {
            return this.prefersDark.matches ? 'dark' : 'light';
        }
        return this.mode;
    }

    #init() {
        this.#apply(this.currentTheme);
        this.#initPerformanceToggle();

        // Checkbox semantics: use change event and treat checked=true as dark mode
        this.themeToggle?.addEventListener('change', () => {
            this.mode = this.themeToggle.checked ? 'dark' : 'light';
            this.currentTheme = this.#resolveTheme();
            this.#apply(this.currentTheme);
            setStorageWithFallback('theme', this.mode);
        });

        // Theme mode cycle: dark -> light -> auto -> dark
        this.themeModeButton?.addEventListener('click', (e) => {
            // Avoid stealing clicks intended for the checkbox itself.
            if (e.target === this.themeToggle) return;
            this.toggle();
        });

        this.prefersDark.addEventListener('change', (e) => {
            if (this.mode !== 'auto') return;
            this.currentTheme = e.matches ? 'dark' : 'light';
            this.#apply(this.currentTheme);
        });
    }

    #initPerformanceToggle() {
        const toggle = dom.performanceToggle;
        const toggleText = dom.performanceToggleText;

        if (!toggle) return;

        // Apply saved state
        if (this.performanceMode) {
            document.documentElement.classList.add('solid-mode');
            toggle.classList.add('active');
            if (toggleText) toggleText.textContent = 'Perf (On)';
        }

        toggle.addEventListener('click', () => {
            this.performanceMode = !this.performanceMode;
            setStorageWithFallback('performanceMode', String(this.performanceMode));

            console.log(`[Phase 2] Performance Mode: ${this.performanceMode ? 'ON' : 'OFF'}`);

            if (this.performanceMode) {
                document.documentElement.classList.add('solid-mode');
                toggle.classList.add('active');
                if (toggleText) toggleText.textContent = 'Perf (On)';
            } else {
                document.documentElement.classList.remove('solid-mode');
                toggle.classList.remove('active');
                if (toggleText) toggleText.textContent = 'Perf';
            }
        });
    }

    toggle() {
        if (this.mode === 'dark') this.mode = 'light';
        else if (this.mode === 'light') this.mode = 'auto';
        else this.mode = 'dark';

        this.currentTheme = this.#resolveTheme();
        this.#apply(this.currentTheme);
        setStorageWithFallback('theme', this.mode);
    }

    #apply(theme) {
        this.currentTheme = theme;
        // CSS only defines html.theme-light; dark is the default (no class)
        document.documentElement.classList.remove('theme-dark', 'theme-light');
        if (theme === 'light') {
            document.documentElement.classList.add('theme-light');
        }

        if (this.themeToggle) {
            this.themeToggle.checked = theme === 'dark';
            // Optional micro-interaction hook
            this.themeToggle.classList.add('rotating');
            setTimeout(() => this.themeToggle?.classList.remove('rotating'), 650);
        }

        if (dom.themeLabel) {
            const labels = {
                dark: 'Dark mode',
                light: 'Light mode',
                auto: `Auto (${theme})`,
            };
            dom.themeLabel.textContent = labels[this.mode] || labels[theme] || 'Theme';
            dom.themeLabel.title = 'Click to cycle theme mode (dark → light → auto)';
        }
    }
}

// --- Speed Chart (Visual Component) ---

class SpeedChart {
    #resizeHandler = null;
    #themeObserver = null;

    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.dataPoints = [];
        this.maxDataPoints = 30; // 30 seconds of data
        this.maxSpeed = 0;

        // Cache colors from CSS variables (theme-responsive)
        this.colors = this.#getColorsFromCSS();

        // Throttled draw function
        this.throttledDraw = domUtils.throttle(this.draw.bind(this), 16); // ~60fps cap

        // Setup canvas size
        this.resizeCanvas();
        this.#attachResizeListener();
        this.#attachThemeChangeListener();
    }

    destroy() {
        if (this.#resizeHandler) {
            window.removeEventListener('resize', this.#resizeHandler);
            this.#resizeHandler = null;
        }
        if (this.#themeObserver) {
            this.#themeObserver.disconnect();
            this.#themeObserver = null;
        }
    }

    #hexToRgba(hex, alpha) {
        hex = hex.replace('#', '');
        if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
        const r = Number.parseInt(hex.substring(0, 2), 16);
        const g = Number.parseInt(hex.substring(2, 4), 16);
        const b = Number.parseInt(hex.substring(4, 6), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    #getColorsFromCSS() {
        const root = document.documentElement;
        const computedStyle = getComputedStyle(root);
        return {
            grid: computedStyle.getPropertyValue('--border').trim() || '#ccc',
            line: computedStyle.getPropertyValue('--focus').trim() || '#007bff',
        };
    }

    #attachThemeChangeListener() {
        this.#themeObserver = new MutationObserver(() => {
            this.colors = this.#getColorsFromCSS();
            if (this.dataPoints.length > 0) this.throttledDraw();
        });
        this.#themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    }

    #attachResizeListener() {
        // Debounce resize to prevent excessive redraws
        this.#resizeHandler = domUtils.debounce(() => this.resizeCanvas(), 250);
        window.addEventListener('resize', this.#resizeHandler);
    }

    resizeCanvas() {
        if (!this.canvas) return;
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.throttledDraw();
    }

    addDataPoint(speed) {
        this.dataPoints.push(speed);
        if (this.dataPoints.length > this.maxDataPoints) this.dataPoints.shift();
        this.maxSpeed = Math.max(...this.dataPoints, this.maxSpeed * 0.95);
        this.throttledDraw();
    }

    draw() {
        if (!this.ctx || this.dataPoints.length === 0) return;
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        const padding = 10;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;

        this.ctx.clearRect(0, 0, width, height);

        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = padding + (chartHeight / 4) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(padding, y);
            this.ctx.lineTo(width - padding, y);
            this.ctx.stroke();
        }

        this.ctx.strokeStyle = this.colors.line;
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();

        let index = 0;
        for (const speed of this.dataPoints) {
            const x = padding + (chartWidth / (this.maxDataPoints - 1)) * index;
            const y = padding + chartHeight - (speed / (this.maxSpeed || 1)) * chartHeight;
            if (index === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
            index++;
        }

        this.ctx.stroke();
        this.ctx.lineTo(width - padding, height - padding);
        this.ctx.lineTo(padding, height - padding);
        this.ctx.closePath();

        const gradient = this.ctx.createLinearGradient(0, padding, 0, height - padding);
        gradient.addColorStop(0, this.#hexToRgba(this.colors.line, 0.2));
        gradient.addColorStop(1, this.#hexToRgba(this.colors.line, 0));
        this.ctx.fillStyle = gradient;
        this.ctx.fill();

        const summary = document.getElementById('speedChartSummary');
        if (summary) {
            const latest = this.dataPoints.at(-1);
            summary.textContent = `Current speed: ${formatters.formatSpeed(latest || 0)}.`;
        }
    }
}

// --- Focus Trap ---

class FocusTrap {
    constructor(element) {
        this.element = element;
        this.focusableSelector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
        this.active = false;
        this.focusables = [];
        this.handleKeydown = this.#onKeydown.bind(this);
    }

    activate() {
        if (!this.element) return;
        this.focusables = Array.from(this.element.querySelectorAll(this.focusableSelector))
            .filter((el) => !el.hasAttribute('hidden'));
        if (this.focusables.length === 0) return;
        this.active = true;
        this.element.addEventListener('keydown', this.handleKeydown);
        this.focusables[0].focus();
    }

    deactivate() {
        if (!this.active) return;
        this.active = false;
        this.element.removeEventListener('keydown', this.handleKeydown);
    }

    #onKeydown(event) {
        if (!this.active || event.key !== 'Tab') return;
        const first = this.focusables[0];
        const last = this.focusables.at(-1);
        if (!first || !last) return;

        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }
}

// --- Professional GUI Enhancements ---

class ProfessionalGUIEnhancements {
    static chartInstance = null;
    static initialized = false;

    static init() {
        if (this.initialized) return;
        this.initialized = true;

        this.initRippleEffects();
        this.initFloatingLabels();
        this.setupConnectionDropdown();
        this.setupCopyButtons();
        this.setupSpeedChart();
        this.setupAdvancedSettingsPanel();
        this.setupDragAndDrop();
        this.setupShortcuts();
        this.setupTroubleshootPanel();
        this.setupBrowserNotifications();
        this.addEnhancementStyles();
        this.setupSparklines();
        // LogInspector setup should happen where LogStore is accessible if needed, but it seems independent enough.
        if (typeof LogInspector !== 'undefined') {
            this.inspector = new LogInspector();
        }
    }

    static setupSparklines() {
        // If SparklineChart is not defined, skip
        if (typeof SparklineChart === 'undefined') return;
        this.sparkBytes = new SparklineChart('sparklineBytes', '#58a6ff');
        this.sparkSpeed = new SparklineChart('sparklineSpeed', '#22d3ee');
    }

    static updateStats(state) {
        if (this.sparkSpeed) this.sparkSpeed.update(state.speed || 0);
        if (this.sparkBytes) this.sparkBytes.update(state.speed || 0); // Visualizing rate on bytes chart too for now
    }

    static initRippleEffects() {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                const x = e.clientX - e.target.offsetLeft;
                const y = e.clientY - e.target.offsetTop;
                const ripples = document.createElement('span');
                ripples.style.left = x + 'px';
                ripples.style.top = y + 'px';
                this.appendChild(ripples);
                setTimeout(() => ripples.remove(), 1000);
            });
        });
    }

    static initFloatingLabels() {
        const inputs = document.querySelectorAll('.input-group input');
        inputs.forEach(input => {
            // Set initial state
            if (input.value.trim() !== '') {
                input.parentElement.classList.add('has-value');
            }
            input.addEventListener('blur', () => {
                if (input.value.trim() !== '') {
                    input.parentElement.classList.add('has-value');
                } else {
                    input.parentElement.classList.remove('has-value');
                }
            });
        });
    }

    static setupConnectionDropdown() {
        const container = document.querySelector('.connection-header');
        const details = document.getElementById('connectionDetails');
        const toggleBtn = document.getElementById('toggleDetailsKey');

        // We can allow clicking the header to toggle, but maybe just a specific button is better?
        // Let's check if the toggle button exists in DOM
        if (toggleBtn && details) {
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                details.hidden = !details.hidden;
                toggleBtn.style.transform = details.hidden ? 'rotate(0deg)' : 'rotate(180deg)';
            });
        } else if (container && details) {
            container.addEventListener('click', (e) => {
                // Don't toggle if clicking inputs/buttons
                if (['INPUT', 'BUTTON'].includes(e.target.tagName)) return;
                details.hidden = !details.hidden;
            });
        }
    }

    static setupCopyButtons() {
        // Looks for any button with data-copy-target attribute
        document.querySelectorAll('[data-copy-target]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const targetId = btn.dataset.copyTarget;
                const targetEl = document.getElementById(targetId);
                if (targetEl) {
                    const text = targetEl.value || targetEl.textContent;
                    const success = await formatters.copyTextToClipboard(text); // Using global helper via formatters or direct? copyTextToClipboard is global in utils
                    // Actually copyTextToClipboard is a global async function in core-utils
                    // Re-checking core-utils: `async function copyTextToClipboard(text)`

                    if (success) {
                        const originalText = btn.innerHTML;
                        btn.innerHTML = '✓ Copied';
                        setTimeout(() => btn.innerHTML = originalText, 2000);
                    }
                }
            });
        });

        // Global copy handler for specific elements
        if (dom.logCopyBtn) {
            // Handled in LogStore normally, but if here...
        }
    }

    static setupSpeedChart() {
        const toggle = dom.toggleSpeedChart;
        const placeholder = dom.speedChartPlaceholder;
        const container = dom.speedChartContainer;

        if (!toggle || !container) return;

        toggle.addEventListener('click', () => {
            container.hidden = !container.hidden;
            if (!container.hidden) {
                // Initialize chart if needed
                if (!this.chartInstance && dom.speedChart) {
                    this.chartInstance = new SpeedChart('speedChart');
                    if (placeholder) placeholder.hidden = true;
                }
                toggle.textContent = 'Hide Graph';
            } else {
                toggle.textContent = 'Show Graph';
            }
        });
    }

    static setupAdvancedSettingsPanel() {
        // Handled by AdvancedSettings class in core.js usually, but UI parts might be here
        // Checking ui.js... it had this.
        // The AdvancedSettings class in App handles the logic.
        // This might just be for the side panel toggle?
        if (dom.settingsToggle && dom.advancedPanel) {
            // Already bound in App.#bindEvents possibly?
            // Let's leave it to App or AdvancedSettings class if possible to avoid duplication.
            // But ui.js had it.
        }
    }

    static setupDragAndDrop() {
        // Visual overlay handling
        const overlay = dom.dragOverlay;
        if (!overlay) return;

        ['dragenter', 'dragover'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                overlay.classList.add('active');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (e.target === overlay || e.target === document.body) {
                    overlay.classList.remove('active');
                }
            });
        });

        overlay.addEventListener('drop', (e) => {
            e.preventDefault();
            overlay.classList.remove('active');
            if (dom.fileInput) {
                dom.fileInput.files = e.dataTransfer.files;
                dom.fileInput.dispatchEvent(new Event('change'));
            }
        });
    }

    static setupShortcuts() {
        // Ctrl+K to focus search
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                dom.logSearchInput?.focus();
            }
            if (e.key === '?') {
                if (document.activeElement.tagName !== 'INPUT') {
                    // Show shortcut modal
                }
            }
        });
    }

    static setupTroubleshootPanel() {
        // Logic for the troubleshoot slide-out
        if (dom.troubleshootChip && dom.troubleshootSheet) {
            dom.troubleshootChip.addEventListener('click', () => {
                dom.troubleshootSheet.classList.add('open');
            });
            dom.closeTroubleshoot?.addEventListener('click', () => {
                dom.troubleshootSheet.classList.remove('open');
            });
        }
    }

    static setupBrowserNotifications() {
        if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
            // User interaction required to request permission usually
        }
    }

    static updateFileCardPreview(file) {
        if (!file) {
            if (dom.fileNameDisplay) dom.fileNameDisplay.textContent = 'No file selected';
            if (dom.fileMetadata) dom.fileMetadata.hidden = true;
            return;
        }

        if (dom.fileNameDisplay) dom.fileNameDisplay.textContent = file.name;
        if (dom.fileMetadata) dom.fileMetadata.hidden = false;
        if (dom.fileTypeBadge) {
            const ext = file.name.split('.').pop();
            dom.fileTypeBadge.textContent = ext.toUpperCase();
        }
        if (dom.fileModified) {
            dom.fileModified.textContent = new Date(file.lastModified).toLocaleDateString();
        }
    }

    static addEnhancementStyles() {
        // Start CSS transitions after load to prevent unstyled flash
        setTimeout(() => {
            document.body.classList.add('transitions-enabled');
        }, 500);
    }
}
