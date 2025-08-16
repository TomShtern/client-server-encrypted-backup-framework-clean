/**
 * Interactive Effects Manager
 * Handles dynamic UI elements: 3D tilt cards, magnetic button glare, and other tactile interactions
 */

export class InteractiveEffectsManager {
    constructor() {
        this.tiltCards = new Set();
        this.magneticButtons = new Set();
        this.isInitialized = false;
        this.rafId = null;
        
        // Throttle mouse movement events
        this.lastMouseUpdate = 0;
        this.mouseUpdateThrottle = 16; // ~60fps
    }

    /**
     * Initialize all interactive effects
     */
    initialize() {
        if (this.isInitialized) {
            return;
        }
        
        try {
            this.setupTiltCards();
            this.setupMagneticButtons();
            this.setupGlobalMouseTracking();
            this.isInitialized = true;
            console.log('[INTERACTIVE_EFFECTS] All interactive effects initialized successfully');
        } catch (error) {
            console.error('[INTERACTIVE_EFFECTS] Failed to initialize:', error);
        }
    }

    /**
     * Setup 3D tilt effects for glass cards
     */
    setupTiltCards() {
        const cards = document.querySelectorAll('.glass-card');
        
        cards.forEach(card => {
            this.tiltCards.add(card);
            
            // Mouse enter - start tilt effect
            card.addEventListener('mouseenter', (e) => {
                card.classList.add('floating');
                this.enableTiltTracking(card);
            });
            
            // Mouse leave - reset tilt
            card.addEventListener('mouseleave', (e) => {
                card.classList.remove('floating');
                this.resetTilt(card);
            });
            
            // Mouse move - update tilt based on position
            card.addEventListener('mousemove', (e) => {
                this.updateTilt(card, e);
            });
        });
        
        console.log(`[INTERACTIVE_EFFECTS] Setup tilt effects for ${cards.length} glass cards`);
    }

    /**
     * Setup magnetic glare effects for cyber buttons
     */
    setupMagneticButtons() {
        const buttons = document.querySelectorAll('.cyber-btn');
        
        buttons.forEach(button => {
            this.magneticButtons.add(button);
            
            // Mouse move - update glare position
            button.addEventListener('mousemove', (e) => {
                this.updateButtonGlare(button, e);
            });
            
            // Mouse leave - hide glare
            button.addEventListener('mouseleave', (e) => {
                this.resetButtonGlare(button);
            });
        });
        
        console.log(`[INTERACTIVE_EFFECTS] Setup magnetic glare for ${buttons.length} cyber buttons`);
    }

    /**
     * Setup global mouse tracking for performance optimization
     */
    setupGlobalMouseTracking() {
        document.addEventListener('mousemove', (e) => {
            const now = performance.now();
            if (now - this.lastMouseUpdate > this.mouseUpdateThrottle) {
                this.lastMouseUpdate = now;
                this.updateGlobalMouseEffects(e);
            }
        });
    }

    /**
     * Update tilt effect based on mouse position
     */
    updateTilt(card, event) {
        const rect = card.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Calculate mouse position relative to card center
        const mouseX = event.clientX - centerX;
        const mouseY = event.clientY - centerY;
        
        // Calculate rotation values (limited to reasonable angles)
        const rotateY = (mouseX / (rect.width / 2)) * 15; // Max 15 degrees
        const rotateX = -(mouseY / (rect.height / 2)) * 15; // Max 15 degrees, inverted
        
        // Apply the transformation with smooth transition
        card.style.setProperty('--tilt-x', `${rotateX}deg`);
        card.style.setProperty('--tilt-y', `${rotateY}deg`);
    }

    /**
     * Reset card tilt to neutral position
     */
    resetTilt(card) {
        card.style.setProperty('--tilt-x', '0deg');
        card.style.setProperty('--tilt-y', '0deg');
    }

    /**
     * Enable tilt tracking for a specific card
     */
    enableTiltTracking(card) {
        card.dataset.tiltActive = 'true';
    }

    /**
     * Update magnetic button glare effect
     */
    updateButtonGlare(button, event) {
        const rect = button.getBoundingClientRect();
        
        // Calculate mouse position relative to button
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        
        // Convert to percentage for CSS custom properties
        const xPercent = (mouseX / rect.width) * 100;
        const yPercent = (mouseY / rect.height) * 100;
        
        // Apply glare position
        button.style.setProperty('--mouse-x', `${xPercent}%`);
        button.style.setProperty('--mouse-y', `${yPercent}%`);
    }

    /**
     * Reset button glare effect
     */
    resetButtonGlare(button) {
        button.style.setProperty('--mouse-x', '50%');
        button.style.setProperty('--mouse-y', '50%');
    }

    /**
     * Global mouse effects update (performance optimized)
     */
    updateGlobalMouseEffects(event) {
        // This method can be used for global cursor effects or particle systems
        // Currently reserved for future enhancements
    }

    /**
     * Add new elements to tracking (for dynamically created elements)
     */
    addTiltCard(card) {
        if (this.tiltCards.has(card)) {
            return;
        }
        
        this.tiltCards.add(card);
        
        card.addEventListener('mouseenter', (e) => {
            card.classList.add('floating');
            this.enableTiltTracking(card);
        });
        
        card.addEventListener('mouseleave', (e) => {
            card.classList.remove('floating');
            this.resetTilt(card);
        });
        
        card.addEventListener('mousemove', (e) => {
            this.updateTilt(card, e);
        });
    }

    /**
     * Add new button to magnetic tracking
     */
    addMagneticButton(button) {
        if (this.magneticButtons.has(button)) {
            return;
        }
        
        this.magneticButtons.add(button);
        
        button.addEventListener('mousemove', (e) => {
            this.updateButtonGlare(button, e);
        });
        
        button.addEventListener('mouseleave', (e) => {
            this.resetButtonGlare(button);
        });
    }

    /**
     * Remove element from tracking
     */
    removeTiltCard(card) {
        this.tiltCards.delete(card);
        this.resetTilt(card);
        card.classList.remove('floating');
    }

    /**
     * Remove button from tracking
     */
    removeMagneticButton(button) {
        this.magneticButtons.delete(button);
        this.resetButtonGlare(button);
    }

    /**
     * Cleanup all effects and event listeners
     */
    cleanup() {
        this.tiltCards.clear();
        this.magneticButtons.clear();
        
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }
        
        this.isInitialized = false;
        console.log('[INTERACTIVE_EFFECTS] Cleanup completed');
    }

    /**
     * Refresh all effects (useful after DOM changes)
     */
    refresh() {
        this.cleanup();
        this.initialize();
    }

    /**
     * Get current statistics
     */
    getStats() {
        return {
            tiltCards: this.tiltCards.size,
            magneticButtons: this.magneticButtons.size,
            isInitialized: this.isInitialized
        };
    }
}

// Export singleton instance
export const interactiveEffects = new InteractiveEffectsManager();
