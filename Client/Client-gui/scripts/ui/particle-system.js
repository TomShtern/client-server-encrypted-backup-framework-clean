class ParticleSystem {
    constructor(app) {
        this.container = app.elements.particleContainer;
        this.particles = [];
        this.maxParticles = 75; // Increased for desktop focus
        this.colors = ['#00FFFF', '#FF00FF', '#00FF00', '#FFFF00', '#FF0040'];
        this.isEnabled = true;
        this.animationId = null;
        this.currentContext = 'idle'; // 'idle', 'connecting', 'transferring', 'complete'
        this.app = app; // Store app reference for context awareness
        
        // Desktop-focused particle optimization
        if (window.innerWidth < 768) {
            this.maxParticles = 25; // Basic mobile support
        } else if (window.innerWidth < 1200) {
            this.maxParticles = 50; // Tablet/small desktop
        } else if (window.innerWidth >= 1440) {
            this.maxParticles = 100; // Large desktop
        } else if (window.innerWidth >= 1920) {
            this.maxParticles = 150; // 4K+ displays
        }
        
        // Context-specific particle configurations
        this.contextConfigs = {
            idle: {
                colors: ['#00FFFF', '#FF00FF', '#00FF00', '#FFFF00'],
                speed: { min: 0.5, max: 2 },
                spawnRate: 0.2,
                size: { min: 1, max: 3 }
            },
            connecting: {
                colors: ['#00FFFF', '#0080FF', '#00BFFF'],
                speed: { min: 1, max: 3 },
                spawnRate: 0.4,
                size: { min: 2, max: 4 }
            },
            transferring: {
                colors: ['#00FF00', '#32FF32', '#00FFFF', '#FF00FF'],
                speed: { min: 2, max: 5 },
                spawnRate: 0.8,
                size: { min: 2, max: 5 }
            },
            complete: {
                colors: ['#00FF00', '#32FF32', '#00FF80'],
                speed: { min: 3, max: 6 },
                spawnRate: 1.0,
                size: { min: 3, max: 6 }
            }
        };
    }

    init() {
        if (!this.container || !this.isEnabled) {
            return;
        }
        
        this.createInitialParticles();
        this.startAnimation();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        console.log('[ParticleSystem] Initialized with', this.maxParticles, 'max particles');
    }

    createInitialParticles() {
        for (let i = 0; i < this.maxParticles * 0.3; i++) {
            this.createParticle();
        }
    }

    createParticle() {
        if (this.particles.length >= this.maxParticles) {
            return null;
        }

        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Use context-aware configuration
        const config = this.contextConfigs[this.currentContext];
        const color = config.colors[Math.floor(Math.random() * config.colors.length)];
        const size = Math.random() * (config.size.max - config.size.min) + config.size.min;
        const startX = Math.random() * window.innerWidth;
        const speed = Math.random() * (config.speed.max - config.speed.min) + config.speed.min;
        const drift = (Math.random() - 0.5) * 2;
        
        particle.style.cssText = `
            left: ${startX}px;
            top: ${window.innerHeight + 10}px;
            background: ${color};
            width: ${size}px;
            height: ${size}px;
            box-shadow: 0 0 ${size * 3}px ${color};
        `;

        const particleData = {
            element: particle,
            x: startX,
            y: window.innerHeight + 10,
            speed: speed,
            drift: drift,
            opacity: Math.random() * 0.5 + 0.5,
            fadeSpeed: Math.random() * 0.02 + 0.01
        };

        this.particles.push(particleData);
        this.container.appendChild(particle);
        
        return particleData;
    }

    updateParticles() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            
            // Update position
            particle.y -= particle.speed;
            particle.x += particle.drift;
            
            // Update opacity for twinkling effect
            particle.opacity += (Math.random() - 0.5) * particle.fadeSpeed;
            particle.opacity = Math.max(0.1, Math.min(1, particle.opacity));
            
            // Apply changes
            particle.element.style.transform = `translate(${particle.x}px, ${particle.y}px)`;
            particle.element.style.opacity = particle.opacity;
            
            // Remove particles that are off-screen
            if (particle.y < -10 || particle.x < -10 || particle.x > window.innerWidth + 10) {
                particle.element.remove();
                this.particles.splice(i, 1);
            }
        }
        
        // Context-aware particle spawning
        const config = this.contextConfigs[this.currentContext];
        if (Math.random() < config.spawnRate && this.particles.length < this.maxParticles) {
            this.createParticle();
        }
    }

    startAnimation() {
        const animate = () => {
            if (this.isEnabled) {
                this.updateParticles();
                this.animationId = requestAnimationFrame(animate);
            }
        };
        animate();
    }

    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    toggle() {
        this.isEnabled = !this.isEnabled;
        if (this.isEnabled) {
            this.startAnimation();
        } else {
            this.stopAnimation();
        }
    }

    destroy() {
        this.stopAnimation();
        this.particles.forEach(particle => particle.element.remove());
        this.particles = [];
    }

    handleResize() {
        // Desktop-focused particle count adjustment
        const oldMax = this.maxParticles;
        if (window.innerWidth < 768) {
            this.maxParticles = 25;
        } else if (window.innerWidth < 1200) {
            this.maxParticles = 50;
        } else if (window.innerWidth >= 1920) {
            this.maxParticles = 150; // 4K+ displays
        } else if (window.innerWidth >= 1440) {
            this.maxParticles = 100; // Large desktop
        } else {
            this.maxParticles = 75; // Standard desktop
        }
        
        // Remove excess particles if screen got smaller
        if (this.maxParticles < oldMax) {
            const particlesToRemove = this.particles.length - this.maxParticles;
            if (particlesToRemove > 0) {
                const removedParticles = this.particles.splice(-particlesToRemove);
                removedParticles.forEach(particle => particle.element.remove());
            }
        }
    }

    // Context management methods for state-aware particles
    setContext(context) {
        if (this.contextConfigs[context] && context !== this.currentContext) {
            console.log(`[ParticleSystem] Context changed: ${this.currentContext} → ${context}`);
            this.currentContext = context;
            
            // Gradually transition existing particles to new context
            this.transitionToContext();
        }
    }

    transitionToContext() {
        // Gradually remove existing particles to make room for new context particles
        const transitionCount = Math.min(10, this.particles.length);
        for (let i = 0; i < transitionCount; i++) {
            if (this.particles[i]) {
                this.particles[i].element.style.transition = 'opacity 0.5s ease-out';
                this.particles[i].element.style.opacity = '0';
                setTimeout(() => {
                    if (this.particles[i]) {
                        this.particles[i].element.remove();
                        this.particles.splice(i, 1);
                    }
                }, 500);
            }
        }
    }

    // Public methods for integration with app states
    onConnectionStart() {
        this.setContext('connecting');
    }

    onTransferStart() {
        this.setContext('transferring');
    }

    onTransferComplete() {
        this.setContext('complete');
        // Return to idle after celebration
        setTimeout(() => {
            this.setContext('idle');
        }, 3000);
    }

    onDisconnect() {
        this.setContext('idle');
    }
}

export { ParticleSystem };