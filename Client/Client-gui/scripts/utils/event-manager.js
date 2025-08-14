import { debugLog } from '../core/debug-utils.js';

class EventListenerManager {
    constructor() {
        this.listeners = new Map(); // Map<string, {element, event, handler, options}>
        
        // Add cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    /**
     * Validate if element is suitable for event listeners
     * @private
     */
    _isValidElement(element, name) {
        // Guard clause for null/undefined element
        if (!element) {
            console.error(`[EventListenerManager] Cannot add listener '${name}': element is null/undefined`);
            return false;
        }
        
        // Guard clause for missing addEventListener
        if (!element.addEventListener) {
            console.error(`[EventListenerManager] Cannot add listener '${name}': element does not support addEventListener`);
            return false;
        }
        
        return true;
    }
    
    add(name, element, event, handler, options = false) {
        // Validate element using guard clauses
        if (!this._isValidElement(element, name)) {
            return null;
        }
        
        // Remove existing listener with the same name
        this.remove(name);
        
        try {
            // Add the new listener
            element.addEventListener(event, handler, options);
            
            // Store for cleanup
            this.listeners.set(name, {
                element,
                event,
                handler,
                options
            });
            
            debugLog(`Event listener '${name}' added for ${event} on ${element.tagName || 'object'}`, 'EVENT_MANAGER');
            return handler;
        } catch (error) {
            console.error(`[EventListenerManager] Failed to add listener '${name}':`, error);
            return null;
        }
    }
    
    remove(name) {
        if (this.listeners.has(name)) {
            const {element, event, handler, options} = this.listeners.get(name);
            element.removeEventListener(event, handler, options);
            this.listeners.delete(name);
            debugLog(`Event listener '${name}' removed`, 'EVENT_MANAGER');
            return true;
        }
        return false;
    }
    
    has(name) {
        return this.listeners.has(name);
    }
    
    cleanup() {
        debugLog('Cleaning up event listeners...', 'EVENT_MANAGER');
        
        // Use for...of loop for better error handling
        for (const [name, listener] of this.listeners) {
            const {element, event, handler, options} = listener;
            try {
                element.removeEventListener(event, handler, options);
                debugLog(`Cleaned up event listener '${name}'`, 'EVENT_MANAGER');
            } catch (error) {
                console.warn(`Failed to clean up event listener '${name}':`, error);
                // Continue with next listener on error
            }
        }
        
        this.listeners.clear();
        debugLog('All event listeners cleaned up', 'EVENT_MANAGER');
    }
    
    getStats() {
        return {
            listenerCount: this.listeners.size,
            listenerNames: Array.from(this.listeners.keys())
        };
    }
}

export { EventListenerManager };