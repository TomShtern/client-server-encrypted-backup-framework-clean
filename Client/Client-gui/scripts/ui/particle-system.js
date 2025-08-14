class ParticleSystem {
    constructor(app) {
        this.container = app.elements.particleContainer;
        this.particles = [];
        this.maxParticles = 50;
        this.colors = ['#00FFFF', '#FF00FF', '#00FF00', '#FFFF00', '#FF0040'];
        this.isEnabled = true;
        this.animationId = null;
        
        // Performance optimization - reduce particles on smaller screens
        if (window.innerWidth < 768) {
            this.maxParticles = 25;
        } else if (window.innerWidth < 1200) {
            this.maxParticles = 35;
        }
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
        
        const color = this.colors[Math.floor(Math.random() * this.colors.length)];
        const size = Math.random() * 3 + 1;
        const startX = Math.random() * window.innerWidth;
        const speed = Math.random() * 2 + 0.5;
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
        
        // Randomly create new particles
        if (Math.random() < 0.3 && this.particles.length < this.maxParticles) {
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
        // Adjust particle count based on screen size
        const oldMax = this.maxParticles;
        if (window.innerWidth < 768) {
            this.maxParticles = 25;
        } else if (window.innerWidth < 1200) {
            this.maxParticles = 35;
        } else {
            this.maxParticles = 50;
        }
        
        // Remove excess particles if screen got smaller
        if (this.maxParticles < oldMax) {
            // Batch remove excess particles for better performance
            const particlesToRemove = this.particles.length - this.maxParticles;
            if (particlesToRemove > 0) {
                const removedParticles = this.particles.splice(-particlesToRemove);
                removedParticles.forEach(particle => particle.element.remove());
            }
        }
    }
}

export { ParticleSystem };