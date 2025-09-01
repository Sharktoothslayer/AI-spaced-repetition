// ========================================
// DOM UTILITY MODULE - Common DOM Operations
// ========================================

const DOM = {
    // Element selectors
    selectors: {
        // Main containers
        appContainer: '.app-container',
        mainContent: '.main-content',
        sidebar: '.sidebar',
        
        // Tab elements
        tabContent: '.tab-content',
        navButton: '.nav-button',
        
        // Chat elements
        chatContainer: '#chat-tab',
        chatMessages: '.chat-messages',
        messageInput: '#messageInput',
        sendButton: '#sendButton',
        vocabularyToggle: '#vocabularyToggle',
        
        // Vocabulary elements
        vocabularyContainer: '#vocabulary-tab',
        wordsList: '#wordsList',
        searchInput: '#searchInput',
        addWordBtn: '#addWordBtn',
        
        // Review elements
        reviewContainer: '#review-tab',
        reviewCard: '.review-card',
        qualityButtons: '.quality-buttons',
        
        // Stats elements
        statsContainer: '#stats-tab',
        statsOverview: '#statsOverview',
        metricsGrid: '#metricsGrid'
    },
    
    // Get element by selector
    get(selector) {
        return document.querySelector(selector);
    },
    
    // Get all elements by selector
    getAll(selector) {
        return document.querySelectorAll(selector);
    },
    
    // Get element by ID
    getById(id) {
        return document.getElementById(id);
    },
    
    // Create element with attributes
    create(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        
        // Set text content
        if (textContent) {
            element.textContent = textContent;
        }
        
        return element;
    },
    
    // Add event listener
    on(element, event, handler, options = {}) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.addEventListener(event, handler, options);
        }
    },
    
    // Remove event listener
    off(element, event, handler) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.removeEventListener(event, handler);
        }
    },
    
    // Show/hide elements
    show(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.style.display = '';
            element.classList.remove('hidden');
        }
    },
    
    hide(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    },
    
    // Toggle visibility
    toggle(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            if (element.style.display === 'none' || element.classList.contains('hidden')) {
                this.show(element);
            } else {
                this.hide(element);
            }
        }
    },
    
    // Add/remove classes
    addClass(element, className) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.classList.add(className);
        }
    },
    
    removeClass(element, className) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.classList.remove(className);
        }
    },
    
    toggleClass(element, className) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.classList.toggle(className);
        }
    },
    
    // Check if element has class
    hasClass(element, className) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        return element && element.classList.contains(className);
    },
    
    // Set/get attributes
    setAttr(element, attr, value) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.setAttribute(attr, value);
        }
    },
    
    getAttr(element, attr) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        return element ? element.getAttribute(attr) : null;
    },
    
    // Set/get text content
    setText(element, text) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.textContent = text;
        }
    },
    
    getText(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        return element ? element.textContent : '';
    },
    
    // Set/get inner HTML
    setHTML(element, html) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.innerHTML = html;
        }
    },
    
    getHTML(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        return element ? element.innerHTML : '';
    },
    
    // Append/prepend elements
    append(parent, child) {
        if (typeof parent === 'string') {
            parent = this.get(parent);
        }
        
        if (parent && child) {
            parent.appendChild(child);
        }
    },
    
    prepend(parent, child) {
        if (typeof parent === 'string') {
            parent = this.get(parent);
        }
        
        if (parent && child) {
            parent.insertBefore(child, parent.firstChild);
        }
    },
    
    // Remove element
    remove(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    },
    
    // Clear element content
    clear(element) {
        if (typeof element === 'string') {
            element = this.get(element);
        }
        
        if (element) {
            element.innerHTML = '';
        }
    },
    
    // Check if element exists
    exists(selector) {
        return !!this.get(selector);
    },
    
    // Wait for element to exist
    waitFor(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = this.get(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            const startTime = Date.now();
            const checkInterval = setInterval(() => {
                const element = this.get(selector);
                if (element) {
                    clearInterval(checkInterval);
                    resolve(element);
                } else if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                }
            }, 100);
        });
    }
};

// Export for use in other modules
window.DOM = DOM;
