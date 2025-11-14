/**
 * Performance Optimizer - RAF-based DOM update batching
 * Prevents layout thrashing by batching DOM updates into single animation frames
 */

class PerformanceOptimizer {
  constructor() {
    this.pendingUpdates = new Map();
    this.rafId = null;
    this.isScheduled = false;
  }

  /**
   * Schedule a DOM update to run in the next animation frame
   * @param {string} key - Unique key for this update
   * @param {Function} updateFn - Function that performs DOM updates
   */
  scheduleUpdate(key, updateFn) {
    this.pendingUpdates.set(key, updateFn);

    if (!this.isScheduled) {
      this.isScheduled = true;
      this.rafId = requestAnimationFrame(() => this.flush());
    }
  }

  /**
   * Execute all pending updates in a single frame
   */
  flush() {
    if (this.pendingUpdates.size === 0) {
      this.isScheduled = false;
      return;
    }

    // Execute all pending updates
    for (const [key, updateFn] of this.pendingUpdates) {
      try {
        updateFn();
      } catch (error) {
        console.error(`Update failed for ${key}:`, error);
      }
    }

    this.pendingUpdates.clear();
    this.isScheduled = false;
  }

  /**
   * Cancel all pending updates
   */
  cancel() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.pendingUpdates.clear();
    this.isScheduled = false;
  }
}

/**
 * Debounce function with RAF optimization
 * @param {Function} fn - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function rafDebounce(fn, wait = 16) {
  let timeoutId = null;
  let rafId = null;

  return function debounced(...args) {
    const later = () => {
      timeoutId = null;
      rafId = requestAnimationFrame(() => {
        fn.apply(this, args);
        rafId = null;
      });
    };

    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (rafId) {
      cancelAnimationFrame(rafId);
    }

    timeoutId = setTimeout(later, wait);
  };
}

/**
 * Throttle function with RAF optimization
 * @param {Function} fn - Function to throttle
 * @param {number} limit - Limit in milliseconds
 * @returns {Function} Throttled function
 */
export function rafThrottle(fn, limit = 16) {
  let inThrottle = false;
  let rafId = null;

  return function throttled(...args) {
    if (!inThrottle) {
      rafId = requestAnimationFrame(() => {
        fn.apply(this, args);
        rafId = null;
      });
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/**
 * Batch DOM reads and writes to prevent layout thrashing
 */
export class DOMBatcher {
  constructor() {
    this.reads = [];
    this.writes = [];
    this.scheduled = false;
  }

  /**
   * Schedule a DOM read operation
   * @param {Function} readFn - Function that reads from the DOM
   * @returns {Promise} Promise that resolves with the read result
   */
  read(readFn) {
    return new Promise((resolve) => {
      this.reads.push(() => {
        const result = readFn();
        resolve(result);
      });
      this.schedule();
    });
  }

  /**
   * Schedule a DOM write operation
   * @param {Function} writeFn - Function that writes to the DOM
   * @returns {Promise} Promise that resolves when write is complete
   */
  write(writeFn) {
    return new Promise((resolve) => {
      this.writes.push(() => {
        writeFn();
        resolve();
      });
      this.schedule();
    });
  }

  /**
   * Schedule the batched execution
   */
  schedule() {
    if (!this.scheduled) {
      this.scheduled = true;
      requestAnimationFrame(() => this.flush());
    }
  }

  /**
   * Execute all batched operations
   */
  flush() {
    // Execute all reads first
    const reads = this.reads.splice(0);
    reads.forEach(read => read());

    // Then execute all writes
    const writes = this.writes.splice(0);
    writes.forEach(write => write());

    this.scheduled = false;
  }
}

/**
 * Smooth value interpolation for animated counters
 */
export class SmoothCounter {
  constructor(element, options = {}) {
    this.element = element;
    this.targetValue = 0;
    this.currentValue = 0;
    this.duration = options.duration || 300;
    this.formatFn = options.formatFn || ((v) => Math.round(v).toString());
    this.rafId = null;
    this.startTime = null;
    this.startValue = 0;
  }

  /**
   * Set a new target value and animate towards it
   * @param {number} value - Target value
   */
  setValue(value) {
    if (value === this.targetValue) return;

    this.startValue = this.currentValue;
    this.targetValue = value;
    this.startTime = null;

    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }

    this.animate();
  }

  /**
   * Animation loop
   */
  animate(timestamp) {
    if (!this.startTime) {
      this.startTime = timestamp;
    }

    const elapsed = timestamp - this.startTime;
    const progress = Math.min(elapsed / this.duration, 1);

    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    this.currentValue = this.startValue + (this.targetValue - this.startValue) * eased;

    this.element.textContent = this.formatFn(this.currentValue);

    if (progress < 1) {
      this.rafId = requestAnimationFrame((t) => this.animate(t));
    } else {
      this.currentValue = this.targetValue;
      this.element.textContent = this.formatFn(this.targetValue);
      this.rafId = null;
    }
  }

  /**
   * Stop animation and set value immediately
   * @param {number} value - Value to set
   */
  setImmediate(value) {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.currentValue = value;
    this.targetValue = value;
    this.element.textContent = this.formatFn(value);
  }

  /**
   * Cleanup
   */
  destroy() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
  }
}

/**
 * Intersection Observer helper for lazy loading/animations
 */
export function createIntersectionObserver(callback, options = {}) {
  const defaultOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
    ...options
  };

  return new IntersectionObserver(callback, defaultOptions);
}

/**
 * Measure performance of a function
 */
export function measurePerformance(label, fn) {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  console.log(`[Performance] ${label}: ${(end - start).toFixed(2)}ms`);
  return result;
}

/**
 * Create a singleton instance
 */
const performanceOptimizer = new PerformanceOptimizer();
const domBatcher = new DOMBatcher();

export { performanceOptimizer, domBatcher };
export default performanceOptimizer;
