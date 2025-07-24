/**
 * NewUI JavaScript Library
 * Provides client-side interactivity for NewUI components
 */

(function(window, document) {
    'use strict';

    const NewUI = {
        version: '0.1.0',
        components: {},
        handlers: {},
        state: {},
        lifecycles: {},
        websocket: null,
        wsHandlers: {},

        /**
         * Initialize NewUI
         */
        init: function() {
            // Set up event delegation
            this.setupEventDelegation();
            
            // Initialize components
            this.initializeComponents();
            
            // Set up state synchronization
            this.setupStateSync();
            
            console.log('NewUI initialized v' + this.version);
        },

        /**
         * Set up global event delegation
         */
        setupEventDelegation: function() {
            // Click events
            document.addEventListener('click', (e) => {
                const target = e.target.closest('[data-ui-click]');
                if (target) {
                    e.preventDefault();
                    this.handleEvent('click', target, e);
                }
            });

            // Submit events
            document.addEventListener('submit', (e) => {
                if (e.target.hasAttribute('data-ui-submit')) {
                    e.preventDefault();
                    this.handleEvent('submit', e.target, e);
                }
            });

            // Change events
            document.addEventListener('change', (e) => {
                const target = e.target.closest('[data-ui-change]');
                if (target) {
                    this.handleEvent('change', target, e);
                }

                // Handle data binding
                if (e.target.hasAttribute('data-ui-bind') || e.target.hasAttribute('data-ui-model')) {
                    this.handleDataBinding(e.target);
                }
            });

            // Input events for real-time binding
            document.addEventListener('input', (e) => {
                if (e.target.hasAttribute('data-ui-bind') || e.target.hasAttribute('data-ui-model')) {
                    this.handleDataBinding(e.target);
                }
            });
        },

        /**
         * Initialize all components on the page
         */
        initializeComponents: function() {
            const components = document.querySelectorAll('[data-ui-component]');
            components.forEach(element => {
                const componentName = element.getAttribute('data-ui-component');
                const stateData = element.getAttribute('data-ui-state');
                
                // Parse state if exists
                let state = {};
                if (stateData) {
                    try {
                        state = JSON.parse(stateData);
                    } catch (e) {
                        console.error('Failed to parse component state:', e);
                    }
                }

                // Generate component ID (respects existing data-ui-id)
                const componentId = this.generateComponentId(element);
                if (!element.hasAttribute('data-ui-id')) {
                    element.setAttribute('data-ui-id', componentId);
                }
                
                // Store state
                this.state[componentId] = state;

                // Fire init lifecycle hook
                this.fireLifecycleHook(componentName, 'init', element, state);

                // Initialize component if handler exists
                if (this.components[componentName]) {
                    this.components[componentName].call(this, element, state);
                }

                // Initialize bound form elements
                this.initializeBoundElements(element, state);
                
                // Initialize conditional rendering
                this.initializeConditionals(element, state);
                
                // Initialize list rendering
                this.initializeLists(element, state);
                
                // Fire mounted lifecycle hook
                this.fireLifecycleHook(componentName, 'mounted', element, state);
            });
        },

        /**
         * Initialize form elements with bound data
         */
        initializeBoundElements: function(component, state) {
            const boundElements = component.querySelectorAll('[data-ui-bind], [data-ui-model]');
            boundElements.forEach(element => {
                const bindPath = element.getAttribute('data-ui-bind') || element.getAttribute('data-ui-model');
                if (bindPath) {
                    const value = this.getStateValue(component.getAttribute('data-ui-id'), bindPath);
                    if (value !== undefined) {
                        if (element.tagName === 'INPUT' || element.tagName === 'SELECT' || element.tagName === 'TEXTAREA') {
                            this.setElementValue(element, value);
                        } else {
                            // For display elements, update text content
                            let displayValue = '';
                            if (value !== null && value !== undefined) {
                                // Handle boolean values
                                if (typeof value === 'boolean') {
                                    displayValue = value ? 'Yes' : 'No';
                                } else {
                                    displayValue = String(value);
                                }
                            }
                            element.textContent = displayValue;
                        }
                    }
                }
            });
        },

        /**
         * Get state value using dot notation
         */
        getStateValue: function(componentId, path) {
            const state = this.state[componentId];
            if (!state) return undefined;

            const parts = path.split('.');
            let value = state;
            
            for (let part of parts) {
                if (value && typeof value === 'object') {
                    value = value[part];
                } else {
                    return undefined;
                }
            }
            
            return value;
        },

        /**
         * Handle UI events
         */
        handleEvent: function(eventType, element, event) {
            const handlerName = element.getAttribute(`data-ui-${eventType}`);
            
            // Check for built-in handlers
            if (this.handlers[handlerName]) {
                // Call handler with NewUI as context, not this
                this.handlers[handlerName].call(window.NewUI, element, event);
                return;
            }

            // Check for AJAX handlers
            if (handlerName.startsWith('ajax:')) {
                const endpoint = handlerName.substring(5);
                this.handleAjaxEvent(endpoint, element, event);
                return;
            }

            // Try to call global function
            if (window[handlerName] && typeof window[handlerName] === 'function') {
                window[handlerName].call(element, event);
            } else {
                console.warn('Handler not found:', handlerName);
            }
        },

        /**
         * Handle AJAX events
         */
        handleAjaxEvent: function(endpoint, element, event) {
            const componentId = this.getComponentId(element);
            const component = element.closest('[data-ui-component]');
            const componentName = component ? component.getAttribute('data-ui-component') : null;

            // Get HTTP method from data-method attribute or default to POST
            const method = element.getAttribute('data-method') || 'POST';

            // Prepare data
            const data = this.collectFormData(element);
            data._component = componentName;
            data._state = this.state[componentId] || {};

            // Show loading state
            this.setLoading(element, true);

            // Make AJAX request
            fetch(endpoint, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-NewUI-Partial': 'true',
                    'X-NewUI-Component': componentName
                },
                body: method === 'GET' || method === 'DELETE' ? null : JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                console.log('Received HTML:', html);
                
                // Find the component to update
                let updateTarget = document.querySelector('[data-ui-component="todo_list"]');
                console.log('Update target:', updateTarget);
                
                if (updateTarget) {
                    updateTarget.outerHTML = html;
                    // Re-initialize the component
                    this.initializeComponents();
                } else {
                    console.error('Could not find todo_list component to update');
                }
                
                // Clear the form if it's a form submission
                if (element.tagName === 'FORM') {
                    element.reset();
                }
                
                // Remove loading state
                this.setLoading(element, false);
            })
            .catch(error => {
                console.error('AJAX request failed:', error);
                this.setLoading(element, false);
            });
        },

        /**
         * Handle two-way data binding
         */
        handleDataBinding: function(element) {
            const bindPath = element.getAttribute('data-ui-bind') || element.getAttribute('data-ui-model');
            const componentId = this.getComponentId(element);
            
            if (!bindPath || !componentId) return;

            // Update state
            const value = this.getElementValue(element);
            this.setStateValue(componentId, bindPath, value);

            // Update other bound elements immediately
            this.updateBoundElements(componentId, bindPath, value, element);
            
            // Update conditionals that might depend on this value
            this.updateConditionals(componentId);

            // Sync with server if configured
            if (element.hasAttribute('data-ui-sync')) {
                // Debounce sync for text inputs
                if (element.type === 'text' || element.type === 'textarea' || element.type === 'email') {
                    this.debouncedSync(componentId);
                } else {
                    this.syncState(componentId);
                }
            }
        },

        /**
         * Get value from form element
         */
        getElementValue: function(element) {
            if (element.type === 'checkbox') {
                return element.checked;
            } else if (element.type === 'radio') {
                return element.checked ? element.value : null;
            } else if (element.tagName === 'SELECT' && element.multiple) {
                return Array.from(element.selectedOptions).map(opt => opt.value);
            } else {
                return element.value;
            }
        },

        /**
         * Set value on form element
         */
        setElementValue: function(element, value) {
            if (element.type === 'checkbox') {
                element.checked = !!value;
            } else if (element.type === 'radio') {
                element.checked = element.value === value;
            } else if (element.tagName === 'SELECT' && element.multiple) {
                Array.from(element.options).forEach(opt => {
                    opt.selected = value && value.includes(opt.value);
                });
            } else {
                element.value = value || '';
            }
        },

        /**
         * Update all elements bound to the same path
         */
        updateBoundElements: function(componentId, bindPath, value, sourceElement) {
            const component = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!component) return;

            const selector = `[data-ui-bind="${bindPath}"], [data-ui-model="${bindPath}"]`;
            const boundElements = component.querySelectorAll(selector);
            
            boundElements.forEach(element => {
                if (element !== sourceElement) {
                    if (element.tagName === 'INPUT' || element.tagName === 'SELECT' || element.tagName === 'TEXTAREA') {
                        this.setElementValue(element, value);
                    } else {
                        // For display elements, update text content
                        let displayValue = '';
                        if (value !== null && value !== undefined) {
                            // Handle boolean values
                            if (typeof value === 'boolean') {
                                displayValue = value ? 'Yes' : 'No';
                            } else {
                                displayValue = String(value);
                            }
                        }
                        element.textContent = displayValue;
                    }
                }
            });
        },

        /**
         * Initialize conditional rendering elements
         */
        initializeConditionals: function(component, state) {
            // Handle show-if conditions
            const showElements = component.querySelectorAll('[data-ui-show]');
            showElements.forEach(element => {
                const condition = element.getAttribute('data-ui-show');
                if (condition) {
                    this.evaluateCondition(component.getAttribute('data-ui-id'), element, condition, 'show');
                }
            });
            
            // Handle hide-if conditions
            const hideElements = component.querySelectorAll('[data-ui-hide]');
            hideElements.forEach(element => {
                const condition = element.getAttribute('data-ui-hide');
                if (condition) {
                    this.evaluateCondition(component.getAttribute('data-ui-id'), element, condition, 'hide');
                }
            });
            
            // Handle toggle conditions
            const toggleElements = component.querySelectorAll('[data-ui-toggle]');
            toggleElements.forEach(element => {
                const condition = element.getAttribute('data-ui-toggle');
                if (condition) {
                    this.evaluateCondition(component.getAttribute('data-ui-id'), element, condition, 'toggle');
                }
            });
        },

        /**
         * Decode HTML entities
         */
        decodeHtmlEntities: function(str) {
            const textarea = document.createElement('textarea');
            textarea.innerHTML = str;
            return textarea.value;
        },

        /**
         * Evaluate a conditional expression
         */
        evaluateCondition: function(componentId, element, condition, type) {
            const state = this.state[componentId] || {};
            let result = false;
            
            // Decode HTML entities in the condition (e.g., &quot; -> ")
            condition = this.decodeHtmlEntities(condition);
            
            try {
                // Create a function that has access to state
                // Use 'with' for simpler property access (note: 'with' is generally discouraged but safe here)
                const evaluator = new Function('state', `
                    with(state) {
                        try {
                            return Boolean(${condition});
                        } catch (e) {
                            return false;
                        }
                    }
                `);
                
                result = evaluator(state);
            } catch (e) {
                // Log error only if it's not about undefined variables
                if (!e.message.includes('is not defined')) {
                    console.error('Error evaluating condition:', condition, e);
                }
                result = false;
            }
            
            // Apply the result based on type
            this.applyConditionalVisibility(element, result, type);
        },

        /**
         * Apply visibility based on condition result
         */
        applyConditionalVisibility: function(element, result, type) {
            switch (type) {
                case 'show':
                    element.style.display = result ? '' : 'none';
                    break;
                case 'hide':
                    element.style.display = result ? 'none' : '';
                    break;
                case 'toggle':
                    // Show/hide child elements based on data-ui-when
                    const trueElement = element.querySelector('[data-ui-when="true"]');
                    const falseElement = element.querySelector('[data-ui-when="false"]');
                    if (trueElement) trueElement.style.display = result ? '' : 'none';
                    if (falseElement) falseElement.style.display = result ? 'none' : '';
                    break;
            }
        },

        /**
         * Update conditionals when state changes
         */
        updateConditionals: function(componentId) {
            const component = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!component) return;
            
            // Re-evaluate all conditionals
            this.initializeConditionals(component, this.state[componentId]);
        },

        /**
         * Initialize list rendering components
         */
        initializeLists: function(component, state) {
            const listElements = component.querySelectorAll('[data-ui-list]');
            listElements.forEach(element => {
                this.renderList(component.getAttribute('data-ui-id'), element);
            });
        },

        /**
         * Render a list component
         */
        renderList: function(componentId, listElement) {
            const itemsPath = listElement.getAttribute('data-ui-list');
            const template = this.decodeHtmlEntities(listElement.getAttribute('data-ui-template') || '');
            const keyProp = listElement.getAttribute('data-ui-key');
            const itemVar = listElement.getAttribute('data-ui-item-var') || 'item';
            const indexVar = listElement.getAttribute('data-ui-index-var') || 'index';
            const emptyMessage = listElement.getAttribute('data-ui-empty') || 'No items';
            
            // Get items from state
            const items = this.getStateValue(componentId, itemsPath) || [];
            
            // Store current DOM state for efficient updates
            const currentKeys = new Map();
            const existingItems = listElement.querySelectorAll('.ui-list-item');
            existingItems.forEach(item => {
                const key = item.getAttribute('data-ui-key');
                if (key) currentKeys.set(key, item);
            });
            
            // Clear the list
            listElement.innerHTML = '';
            
            if (!Array.isArray(items) || items.length === 0) {
                // Show empty message
                listElement.innerHTML = `<div class="ui-list-empty">${emptyMessage}</div>`;
                return;
            }
            
            // Render each item
            items.forEach((item, index) => {
                let itemKey = null;
                if (keyProp && item[keyProp] !== undefined) {
                    itemKey = String(item[keyProp]);
                }
                
                // Try to reuse existing element if key matches
                let itemElement = null;
                if (itemKey && currentKeys.has(itemKey)) {
                    itemElement = currentKeys.get(itemKey);
                    currentKeys.delete(itemKey); // Mark as used
                } else {
                    // Create new element
                    itemElement = document.createElement('div');
                    itemElement.className = 'ui-list-item';
                    if (itemKey) {
                        itemElement.setAttribute('data-ui-key', itemKey);
                    }
                }
                
                // Render the template with item data
                if (template) {
                    const renderedContent = this.renderTemplate(template, {
                        [itemVar]: item,
                        [indexVar]: index,
                        ...item // Spread item properties for direct access
                    });
                    itemElement.innerHTML = renderedContent;
                    
                    // Process any data bindings in the rendered content
                    this.processListItemBindings(itemElement, componentId, itemsPath, index);
                    
                    // Handle checkboxes with data-checked attribute
                    const checkboxes = itemElement.querySelectorAll('input[type="checkbox"][data-checked]');
                    checkboxes.forEach(checkbox => {
                        const checked = checkbox.getAttribute('data-checked') === 'true';
                        checkbox.checked = checked;
                    });
                    
                    // Re-initialize the element to ensure event handlers work
                    this.initializeBoundElements(itemElement, this.state[componentId]);
                }
                
                listElement.appendChild(itemElement);
            });
            
            // Remove any unused elements
            currentKeys.forEach(unusedElement => {
                unusedElement.remove();
            });
        },

        /**
         * Render a template with data
         */
        renderTemplate: function(template, data) {
            // First handle conditional attributes like {completed ? 'checked' : ''}
            template = template.replace(/\{([^}]+)\s*\?\s*'([^']*)'\s*:\s*'([^']*)'\}/g, (match, condition, trueVal, falseVal) => {
                const value = this.getValueByPath(data, condition);
                return value ? trueVal : falseVal;
            });
            
            // Then handle simple variable substitution
            return template.replace(/\{([^}]+)\}/g, (match, path) => {
                // Handle .length property for arrays
                if (path.endsWith('.length')) {
                    const arrayPath = path.slice(0, -7); // Remove '.length'
                    const array = this.getValueByPath(data, arrayPath);
                    return Array.isArray(array) ? array.length : 0;
                }
                
                const value = this.getValueByPath(data, path);
                return value !== undefined ? value : '';
            });
        },

        /**
         * Get value by dot notation path from object
         */
        getValueByPath: function(obj, path) {
            const parts = path.split('.');
            let value = obj;
            
            for (let part of parts) {
                if (value && typeof value === 'object') {
                    value = value[part];
                } else {
                    return undefined;
                }
            }
            
            return value;
        },

        /**
         * Process data bindings within a list item
         */
        processListItemBindings: function(itemElement, componentId, itemsPath, index) {
            // Update any data-ui-bind attributes to include the array index
            const bindElements = itemElement.querySelectorAll('[data-ui-bind], [data-ui-model]');
            bindElements.forEach(element => {
                const originalBinding = element.getAttribute('data-ui-bind') || element.getAttribute('data-ui-model');
                if (originalBinding && !originalBinding.includes('[')) {
                    // Update binding to include the list path and index
                    const newBinding = `${itemsPath}[${index}].${originalBinding}`;
                    if (element.hasAttribute('data-ui-bind')) {
                        element.setAttribute('data-ui-bind', newBinding);
                    } else {
                        element.setAttribute('data-ui-model', newBinding);
                    }
                }
            });
            
            // Initialize bindings for this item
            this.initializeBoundElements(itemElement, this.state[componentId]);
        },

        /**
         * Update lists when state changes
         */
        updateLists: function(componentId, changedPath) {
            const component = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!component) return;
            
            // Find all lists that might be affected
            const lists = component.querySelectorAll('[data-ui-list]');
            lists.forEach(listElement => {
                const itemsPath = listElement.getAttribute('data-ui-list');
                // Re-render if the changed path affects this list
                if (changedPath.startsWith(itemsPath) || itemsPath.startsWith(changedPath)) {
                    this.renderList(componentId, listElement);
                }
            });
        },

        /**
         * Lifecycle hook management
         */
        registerLifecycle: function(componentName, hooks) {
            if (!this.lifecycles[componentName]) {
                this.lifecycles[componentName] = {};
            }
            Object.assign(this.lifecycles[componentName], hooks);
        },

        fireLifecycleHook: function(componentName, hookName, element, state) {
            const hooks = this.lifecycles[componentName];
            if (hooks && hooks[hookName]) {
                try {
                    hooks[hookName].call(this, element, state);
                } catch (e) {
                    console.error(`Error in ${componentName}.${hookName} lifecycle hook:`, e);
                }
            }
        },

        /**
         * Update lifecycle - called when state changes
         */
        notifyComponentUpdate: function(componentId, changedPath, oldValue, newValue) {
            const element = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!element) return;
            
            const componentName = element.getAttribute('data-ui-component');
            const state = this.state[componentId];
            
            this.fireLifecycleHook(componentName, 'beforeUpdate', element, {
                state,
                changedPath,
                oldValue,
                newValue
            });
            
            // Allow hook to prevent update by returning false
            const hooks = this.lifecycles[componentName];
            if (hooks && hooks.beforeUpdate) {
                const result = hooks.beforeUpdate.call(this, element, {
                    state,
                    changedPath,
                    oldValue,
                    newValue
                });
                if (result === false) return;
            }
            
            // After DOM updates
            setTimeout(() => {
                this.fireLifecycleHook(componentName, 'updated', element, {
                    state,
                    changedPath,
                    oldValue,
                    newValue
                });
            }, 0);
        },

        /**
         * Destroy component
         */
        destroyComponent: function(componentId) {
            const element = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!element) return;
            
            const componentName = element.getAttribute('data-ui-component');
            const state = this.state[componentId];
            
            // Fire destroyed hook
            this.fireLifecycleHook(componentName, 'beforeDestroy', element, state);
            
            // Clean up state
            delete this.state[componentId];
            
            // Remove element
            element.remove();
            
            // Fire destroyed hook
            this.fireLifecycleHook(componentName, 'destroyed', element, state);
        },

        /**
         * Debounced sync function
         */
        debouncedSync: function(componentId) {
            if (!this._syncTimers) {
                this._syncTimers = {};
            }
            
            if (this._syncTimers[componentId]) {
                clearTimeout(this._syncTimers[componentId]);
            }
            
            this._syncTimers[componentId] = setTimeout(() => {
                this.syncState(componentId);
                delete this._syncTimers[componentId];
            }, 300);
        },

        /**
         * Set state value using dot notation
         */
        setStateValue: function(componentId, path, value) {
            if (!this.state[componentId]) {
                this.state[componentId] = {};
            }

            // Get old value for lifecycle hooks
            const oldValue = this.getStateValue(componentId, path);
            
            // Handle array notation (e.g., "items[0].name")
            const parts = path.split(/[\.\[\]]+/).filter(p => p);
            let obj = this.state[componentId];
            
            for (let i = 0; i < parts.length - 1; i++) {
                const part = parts[i];
                const nextPart = parts[i + 1];
                
                // Check if next part is a number (array index)
                if (!isNaN(nextPart)) {
                    if (!Array.isArray(obj[part])) {
                        obj[part] = [];
                    }
                    obj = obj[part];
                } else {
                    if (!obj[part]) {
                        obj[part] = {};
                    }
                    obj = obj[part];
                }
            }
            
            obj[parts[parts.length - 1]] = value;
            
            // Update bound elements immediately
            this.updateBoundElements(componentId, path, value);
            
            // Update conditionals that might depend on this value
            this.updateConditionals(componentId);
            
            // Notify component of update
            this.notifyComponentUpdate(componentId, path, oldValue, value);
            
            // Check if this affects any lists
            this.updateLists(componentId, path);
        },

        /**
         * Sync state with server
         */
        syncState: function(componentId, callback) {
            const state = this.state[componentId];
            if (!state) return;

            fetch(`/ui/state/${componentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(state)
            })
            .then(response => response.json())
            .then(data => {
                if (callback) callback(data);
            })
            .catch(error => {
                console.error('State sync failed:', error);
            });
        },

        /**
         * Set up automatic state synchronization
         */
        setupStateSync: function() {
            // Sync state periodically if configured
            const syncInterval = window.NEWUI_SYNC_INTERVAL || 0;
            if (syncInterval > 0) {
                setInterval(() => {
                    Object.keys(this.state).forEach(componentId => {
                        this.syncState(componentId);
                    });
                }, syncInterval);
            }
        },

        /**
         * Utility functions
         */
        generateComponentId: function(element) {
            return element.getAttribute('data-ui-id') || 
                   'ui-' + Math.random().toString(36).substr(2, 9);
        },

        getComponentId: function(element) {
            // First try to find a component with data-ui-component attribute
            const component = element.closest('[data-ui-component][data-ui-id]');
            if (component) {
                return component.getAttribute('data-ui-id');
            }
            // Fallback to any element with data-ui-id
            const fallback = element.closest('[data-ui-id]');
            return fallback ? fallback.getAttribute('data-ui-id') : null;
        },

        collectFormData: function(element) {
            const form = element.tagName === 'FORM' ? element : element.closest('form');
            if (!form) return {};

            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            return data;
        },

        setLoading: function(element, loading) {
            // For forms, find the submit button
            let loadingTarget = element;
            if (element.tagName === 'FORM') {
                loadingTarget = element.querySelector('button[type="submit"], input[type="submit"]');
            }
            
            if (!loadingTarget) return;
            
            if (loading) {
                loadingTarget.classList.add('ui-loading');
                if (loadingTarget.disabled !== undefined) {
                    loadingTarget.disabled = true;
                }
            } else {
                loadingTarget.classList.remove('ui-loading');
                if (loadingTarget.disabled !== undefined) {
                    loadingTarget.disabled = false;
                }
            }
        },

        /**
         * Loading state management
         */
        showLoading: function(elementOrId, options = {}) {
            const element = typeof elementOrId === 'string' 
                ? document.getElementById(elementOrId) 
                : elementOrId;
            
            if (!element) return;

            const {
                type = 'spinner',
                text = 'Loading...',
                overlay = false,
                preserve = false
            } = options;

            // Add loading class
            element.classList.add('ui-loading');

            // Handle loading wrapper
            if (element.classList.contains('loading-wrapper')) {
                const loadingState = element.querySelector('.loading-state');
                const contentState = element.querySelector('.content-state');
                
                if (loadingState && contentState) {
                    loadingState.style.display = 'flex';
                    if (!preserve) {
                        contentState.style.display = 'none';
                    }
                }
            }
            // Handle overlay loading
            else if (overlay) {
                this.showLoadingOverlay(element, text);
            }
            
            // Fire loading lifecycle event
            const componentId = this.getComponentId(element);
            if (componentId) {
                const component = element.closest('[data-ui-component]');
                const componentName = component?.getAttribute('data-ui-component');
                this.fireLifecycleHook(componentName, 'loadingStart', element, { type, text });
            }
        },

        hideLoading: function(elementOrId) {
            const element = typeof elementOrId === 'string' 
                ? document.getElementById(elementOrId) 
                : elementOrId;
            
            if (!element) return;

            // Remove loading class
            element.classList.remove('ui-loading');

            // Handle loading wrapper
            if (element.classList.contains('loading-wrapper')) {
                const loadingState = element.querySelector('.loading-state');
                const contentState = element.querySelector('.content-state');
                
                if (loadingState && contentState) {
                    loadingState.style.display = 'none';
                    contentState.style.display = '';
                }
            }
            // Remove overlay loading
            else {
                this.hideLoadingOverlay(element);
            }
            
            // Fire loading lifecycle event
            const componentId = this.getComponentId(element);
            if (componentId) {
                const component = element.closest('[data-ui-component]');
                const componentName = component?.getAttribute('data-ui-component');
                this.fireLifecycleHook(componentName, 'loadingEnd', element, {});
            }
        },

        showLoadingOverlay: function(element, text = 'Loading...') {
            // Remove existing overlay
            this.hideLoadingOverlay(element);
            
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay ui-loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>${text}</div>
                </div>
            `;
            
            // Make element relative if not already positioned
            const computedStyle = window.getComputedStyle(element);
            if (computedStyle.position === 'static') {
                element.style.position = 'relative';
                overlay.setAttribute('data-ui-restore-position', 'true');
            }
            
            element.appendChild(overlay);
            
            // Fade in animation
            requestAnimationFrame(() => {
                overlay.classList.add('ui-loading-fade-enter-active');
            });
        },

        hideLoadingOverlay: function(element) {
            const overlay = element.querySelector('.ui-loading-overlay');
            if (overlay) {
                overlay.classList.add('ui-loading-fade-exit-active');
                
                setTimeout(() => {
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                    
                    // Restore position if we changed it
                    if (overlay.getAttribute('data-ui-restore-position')) {
                        element.style.position = '';
                    }
                }, 300);
            }
        },

        /**
         * Show loading state for specific duration
         */
        showLoadingFor: function(elementOrId, duration, options = {}) {
            this.showLoading(elementOrId, options);
            
            setTimeout(() => {
                this.hideLoading(elementOrId);
            }, duration);
        },

        /**
         * Toggle button loading state
         */
        setButtonLoading: function(button, loading, text = 'Loading...') {
            if (typeof button === 'string') {
                button = document.getElementById(button) || document.querySelector(button);
            }
            
            if (!button) return;

            if (loading) {
                // Store original text and state
                if (!button.hasAttribute('data-ui-original-text')) {
                    button.setAttribute('data-ui-original-text', button.textContent);
                    button.setAttribute('data-ui-original-disabled', button.disabled);
                }
                
                // Set loading state
                button.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    ${text}
                `;
                button.disabled = true;
                button.classList.add('ui-loading');
            } else {
                // Restore original state
                const originalText = button.getAttribute('data-ui-original-text');
                const originalDisabled = button.getAttribute('data-ui-original-disabled') === 'true';
                
                if (originalText) {
                    button.textContent = originalText;
                    button.disabled = originalDisabled;
                    button.removeAttribute('data-ui-original-text');
                    button.removeAttribute('data-ui-original-disabled');
                }
                
                button.classList.remove('ui-loading');
            }
        },

        /**
         * WebSocket functionality
         */
        connectWebSocket: function(url, options = {}) {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                console.warn('WebSocket already connected');
                return;
            }

            const {
                reconnect = true,
                reconnectInterval = 3000,
                maxReconnectAttempts = 5,
                onOpen = null,
                onClose = null,
                onError = null
            } = options;

            let reconnectAttempts = 0;

            const connect = () => {
                try {
                    this.websocket = new WebSocket(url);

                    this.websocket.onopen = (event) => {
                        console.log('WebSocket connected');
                        reconnectAttempts = 0;
                        if (onOpen) onOpen(event);
                        this.fireWebSocketEvent('open', event);
                    };

                    this.websocket.onmessage = (event) => {
                        this.handleWebSocketMessage(event);
                    };

                    this.websocket.onclose = (event) => {
                        console.log('WebSocket closed');
                        if (onClose) onClose(event);
                        this.fireWebSocketEvent('close', event);

                        // Attempt reconnection
                        if (reconnect && reconnectAttempts < maxReconnectAttempts && !event.wasClean) {
                            reconnectAttempts++;
                            console.log(`Reconnecting WebSocket (attempt ${reconnectAttempts}/${maxReconnectAttempts})...`);
                            setTimeout(connect, reconnectInterval);
                        }
                    };

                    this.websocket.onerror = (event) => {
                        console.error('WebSocket error:', event);
                        if (onError) onError(event);
                        this.fireWebSocketEvent('error', event);
                    };

                } catch (error) {
                    console.error('Failed to create WebSocket connection:', error);
                }
            };

            connect();
        },

        disconnectWebSocket: function() {
            if (this.websocket) {
                this.websocket.close(1000, 'User disconnected');
                this.websocket = null;
            }
        },

        sendWebSocketMessage: function(type, data = {}) {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                console.warn('WebSocket not connected');
                return false;
            }

            const message = {
                type: type,
                data: data,
                timestamp: Date.now()
            };

            this.websocket.send(JSON.stringify(message));
            return true;
        },

        handleWebSocketMessage: function(event) {
            try {
                const message = JSON.parse(event.data);
                const { type, data, componentId } = message;

                // Handle different message types
                switch (type) {
                    case 'state_update':
                        this.handleStateUpdate(componentId, data);
                        break;
                    case 'component_update':
                        this.handleComponentUpdate(componentId, data);
                        break;
                    case 'broadcast':
                        this.handleBroadcast(data);
                        break;
                    case 'custom':
                        this.handleCustomMessage(data);
                        break;
                    default:
                        console.warn('Unknown WebSocket message type:', type);
                }

                // Fire custom handlers
                this.fireWebSocketEvent('message', message);

            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        },

        handleStateUpdate: function(componentId, stateData) {
            if (!componentId || !stateData) return;

            const element = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!element) return;

            // Update component state
            this.state[componentId] = { ...this.state[componentId], ...stateData };

            // Re-initialize bound elements with new state
            this.initializeBoundElements(element, this.state[componentId]);
            this.updateConditionals(componentId);
            this.updateLists(componentId, ''); // Update all lists

            console.log(`WebSocket state update for ${componentId}:`, stateData);
        },

        handleComponentUpdate: function(componentId, htmlData) {
            if (!componentId || !htmlData) return;

            const element = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!element) return;

            const componentName = element.getAttribute('data-ui-component');

            // Fire before update lifecycle
            this.fireLifecycleHook(componentName, 'beforeUpdate', element, {
                state: this.state[componentId],
                source: 'websocket'
            });

            // Update the element HTML
            element.outerHTML = htmlData;

            // Re-initialize the updated component
            this.initializeComponents();

            console.log(`WebSocket component update for ${componentId}`);
        },

        handleBroadcast: function(data) {
            // Handle broadcast messages (e.g., notifications, global updates)
            this.fireWebSocketEvent('broadcast', data);
            console.log('WebSocket broadcast:', data);
        },

        handleCustomMessage: function(data) {
            // Handle custom application-specific messages
            this.fireWebSocketEvent('custom', data);
            console.log('WebSocket custom message:', data);
        },

        registerWebSocketHandler: function(event, handler) {
            if (!this.wsHandlers[event]) {
                this.wsHandlers[event] = [];
            }
            this.wsHandlers[event].push(handler);
        },

        fireWebSocketEvent: function(event, data) {
            if (this.wsHandlers[event]) {
                this.wsHandlers[event].forEach(handler => {
                    try {
                        handler.call(this, data);
                    } catch (error) {
                        console.error(`Error in WebSocket ${event} handler:`, error);
                    }
                });
            }
        },

        subscribeToComponent: function(componentId) {
            this.sendWebSocketMessage('subscribe', { componentId });
        },

        unsubscribeFromComponent: function(componentId) {
            this.sendWebSocketMessage('unsubscribe', { componentId });
        },

        /**
         * Public API for registering components and handlers
         */
        registerComponent: function(name, handler) {
            this.components[name] = handler;
        },

        registerHandler: function(name, handler) {
            this.handlers[name] = handler;
        },

        /**
         * Update component via AJAX
         */
        updateComponent: function(componentId, data, callback) {
            const element = document.querySelector(`[data-ui-id="${componentId}"]`);
            if (!element) return;

            const componentName = element.getAttribute('data-ui-component');
            
            fetch(`/ui/partial/${componentName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-NewUI-Partial': 'true'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.text())
            .then(html => {
                element.outerHTML = html;
                this.initializeComponents();
                if (callback) callback();
            })
            .catch(error => {
                console.error('Component update failed:', error);
            });
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => NewUI.init());
    } else {
        NewUI.init();
    }

    // Export to global scope
    window.NewUI = NewUI;

})(window, document);