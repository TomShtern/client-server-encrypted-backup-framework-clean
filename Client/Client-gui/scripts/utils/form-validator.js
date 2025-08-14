class FormValidator {
    constructor() {
        this.rules = new Map();
        this.validators = {
            required: (value) => value && value.trim().length > 0,
            serverAddress: (value) => {
                if (!value) {
                    return false;
                }
                const parts = value.split(':');
                if (parts.length !== 2) {
                    return false;
                }
                const [ip, port] = parts;
                const portNum = parseInt(port);
                return ip.length > 0 && portNum > 0 && portNum <= 65535;
            },
            username: (value) => {
                if (!value) {
                    return false;
                }
                return /^[a-zA-Z0-9_-]{2,32}$/.test(value);
            }
        };
    }

    /**
     * Add validation rule to a field
     */
    addRule(fieldId, validatorName, message, required = true) {
        if (!this.rules.has(fieldId)) {
            this.rules.set(fieldId, []);
        }
        this.rules.get(fieldId).push({
            validator: validatorName,
            message: message,
            required: required
        });
    }

    /**
     * Validate a single field
     */
    validateField(fieldId, value) {
        const rules = this.rules.get(fieldId);
        if (!rules) {
            return { isValid: true, message: '' };
        }

        for (const rule of rules) {
            const validator = this.validators[rule.validator];
            if (validator && !validator(value)) {
                return { 
                    isValid: false, 
                    message: rule.message,
                    level: rule.required ? 'invalid' : 'warning'
                };
            }
        }

        return { isValid: true, message: 'Valid input', level: 'valid' };
    }

    /**
     * Apply visual validation state to field
     */
    applyValidationState(fieldElement, state) {
        if (!fieldElement) {
            return;
        }

        // Remove existing states
        fieldElement.classList.remove('valid', 'invalid', 'warning');
        
        // Add new state
        if (state.level) {
            fieldElement.classList.add(state.level);
        }

        // Update validation icon and helper text
        this.updateValidationUI(fieldElement, state);
    }

    /**
     * Update validation UI elements
     */
    updateValidationUI(fieldElement, state) {
        const container = fieldElement.closest('.form-field') || fieldElement.parentElement;
        if (!container) {
            return;
        }

        // Update or create validation icon
        let icon = container.querySelector('.validation-icon');
        if (!icon && state.level !== 'valid') {
            icon = document.createElement('span');
            icon.className = 'validation-icon';
            container.appendChild(icon);
        }

        if (icon) {
            icon.className = `validation-icon ${state.level}`;
            icon.textContent = this.getValidationIcon(state.level);
            icon.style.display = state.level === 'valid' ? 'none' : 'block';
        }

        // Update or create helper text
        let helper = container.querySelector('.validation-helper');
        if (!helper && state.message) {
            helper = document.createElement('div');
            helper.className = 'validation-helper';
            container.appendChild(helper);
        }

        if (helper && state.message) {
            helper.className = `validation-helper ${state.level} show`;
            helper.textContent = state.message;
        } else if (helper) {
            helper.classList.remove('show');
        }
    }

    /**
     * Get validation icon for state
     */
    getValidationIcon(level) {
        const icons = {
            valid: '✓',
            invalid: '✗',
            warning: '⚠'
        };
        return icons[level] || '';
    }

    /**
     * Setup real-time validation for a field
     */
    setupRealTimeValidation(fieldElement, fieldId) {
        if (!fieldElement) {
            return;
        }

        const validateAndUpdate = () => {
            const { value } = fieldElement;
            const state = this.validateField(fieldId, value);
            this.applyValidationState(fieldElement, state);
        };

        // Validate on input (real-time)
        fieldElement.addEventListener('input', validateAndUpdate);
        
        // Validate on blur
        fieldElement.addEventListener('blur', validateAndUpdate);

        // Initial validation
        validateAndUpdate();
    }
}

export { FormValidator };