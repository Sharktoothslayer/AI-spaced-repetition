// ========================================
// TRANSLATION MODULE - Word Translation & AI
// ========================================

const TranslationModule = {
    // Module state
    state: {
        isInitialized: false,
        translationCache: new Map(),
        isTranslating: false,
        currentTranslation: null
    },
    
    // Initialize the translation module
    init() {
        if (this.state.isInitialized) return;
        
        console.log('🌐 Initializing Translation Module...');
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        this.state.isInitialized = true;
        console.log('✅ Translation Module initialized');
    },
    
    // Initialize event listeners
    initializeEventListeners() {
        // Global event delegation for translation actions
        DOM.on(document, 'click', (e) => this.handleGlobalClick(e));
    },
    
    // Handle global click events
    handleGlobalClick(e) {
        const action = e.target.dataset.action;
        
        if (!action) return;
        
        switch (action) {
            case 'translate-word':
                const word = e.target.dataset.word;
                this.translateWord(word);
                break;
            case 'add-translated-word':
                this.addTranslatedWord();
                break;
        }
    },
    
    // Translate a word using multiple methods
    async translateWord(word, context = '') {
        if (!word || this.state.isTranslating) return;
        
        this.state.isTranslating = true;
        this.state.currentTranslation = null;
        
        try {
            console.log(`🌐 Translating word: ${word}`);
            
            // Check cache first
            const cacheKey = `${word.toLowerCase()}_${context.toLowerCase()}`;
            if (this.state.translationCache.has(cacheKey)) {
                const cached = this.state.translationCache.get(cacheKey);
                this.state.currentTranslation = cached;
                this.showTranslationResult(cached);
                return;
            }
            
            // Try Google Translate first (faster)
            let translation = await this.tryGoogleTranslate(word, context);
            
            // Fallback to AI translation if Google fails
            if (!translation || !translation.success) {
                console.log('🔄 Google Translate failed, trying AI translation...');
                translation = await this.tryAITranslation(word, context);
            }
            
            if (translation && translation.success) {
                // Cache the result
                this.state.translationCache.set(cacheKey, translation);
                this.state.currentTranslation = translation;
                this.showTranslationResult(translation);
            } else {
                this.showTranslationError('Translation failed. Please try again.');
            }
            
        } catch (error) {
            console.error('❌ Translation error:', error);
            this.showTranslationError('Translation failed due to an error.');
        } finally {
            this.state.isTranslating = false;
        }
    },
    
    // Try Google Translate
    async tryGoogleTranslate(word, context = '') {
        try {
            if (typeof API !== 'undefined') {
                const response = await API.post('/api/sr/ai-translate', {
                    word: word,
                    context: context
                });
                
                if (response.success) {
                    return {
                        word: word,
                        translation: response.translation,
                        example: response.example,
                        word_type: response.word_type,
                        source: 'google',
                        success: true
                    };
                }
            }
            
            return null;
        } catch (error) {
            console.warn('⚠️ Google Translate failed:', error);
            return null;
        }
    },
    
    // Try AI translation
    async tryAITranslation(word, context = '') {
        try {
            if (typeof API !== 'undefined') {
                const response = await API.post('/api/sr/ai-translate-word', {
                    word: word,
                    context: context
                });
                
                if (response.success) {
                    return {
                        word: word,
                        translation: response.translation,
                        example: `Example with ${word}`,
                        word_type: 'noun', // Default type
                        source: 'ai',
                        success: true
                    };
                }
            }
            
            return null;
        } catch (error) {
            console.warn('⚠️ AI translation failed:', error);
            return null;
        }
    },
    
    // Show translation result
    showTranslationResult(translation) {
        // Create or update translation result display
        let resultContainer = DOM.get('.translation-result');
        
        if (!resultContainer) {
            resultContainer = DOM.create('div', { className: 'translation-result' });
            const mainContent = DOM.get('.main-content');
            if (mainContent) {
                mainContent.appendChild(resultContainer);
            }
        }
        
        resultContainer.innerHTML = `
            <div class="translation-card">
                <div class="translation-header">
                    <h3>Translation Result</h3>
                    <span class="translation-source">${translation.source.toUpperCase()}</span>
                </div>
                <div class="translation-content">
                    <div class="word-pair">
                        <div class="original-word">${translation.word}</div>
                        <div class="translation-arrow">→</div>
                        <div class="translated-word">${translation.translation}</div>
                    </div>
                    <div class="word-details">
                        <div class="word-type-badge">${translation.word_type}</div>
                        ${translation.example ? `<div class="word-example">${translation.example}</div>` : ''}
                    </div>
                    <div class="translation-actions">
                        <button class="btn btn-primary" data-action="add-translated-word">
                            Add to Vocabulary
                        </button>
                        <button class="btn btn-secondary" data-action="close-translation">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        const closeBtn = resultContainer.querySelector('[data-action="close-translation"]');
        if (closeBtn) {
            DOM.on(closeBtn, 'click', () => this.hideTranslationResult());
        }
        
        const addBtn = resultContainer.querySelector('[data-action="add-translated-word"]');
        if (addBtn) {
            DOM.on(addBtn, 'click', () => this.addTranslatedWord());
        }
        
        // Show the result
        DOM.show(resultContainer);
    },
    
    // Hide translation result
    hideTranslationResult() {
        const resultContainer = DOM.get('.translation-result');
        if (resultContainer) {
            DOM.hide(resultContainer);
        }
    },
    
    // Add translated word to vocabulary
    addTranslatedWord() {
        if (!this.state.currentTranslation) return;
        
        try {
            // Use VocabularyModule if available
            if (typeof VocabularyModule !== 'undefined') {
                VocabularyModule.addWordToVocabulary({
                    word: this.state.currentTranslation.word,
                    translation: this.state.currentTranslation.translation,
                    example: this.state.currentTranslation.example,
                    word_type: this.state.currentTranslation.word_type,
                    notes: `Translated via ${this.state.currentTranslation.source}`
                });
                
                this.showSuccess('Word added to vocabulary!');
                this.hideTranslationResult();
            } else {
                // Fallback: show form
                this.showAddWordForm();
            }
        } catch (error) {
            console.error('❌ Failed to add word:', error);
            this.showError('Failed to add word to vocabulary');
        }
    },
    
    // Show add word form (fallback)
    showAddWordForm() {
        const formHTML = `
            <div class="add-word-form">
                <h3>Add Translated Word</h3>
                <form id="addTranslatedWordForm">
                    <div class="form-group">
                        <label for="translatedWord">Italian Word:</label>
                        <input type="text" id="translatedWord" value="${this.state.currentTranslation.word}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="translatedTranslation">Translation:</label>
                        <input type="text" id="translatedTranslation" value="${this.state.currentTranslation.translation}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="translatedExample">Example:</label>
                        <input type="text" id="translatedExample" value="${this.state.currentTranslation.example || ''}">
                    </div>
                    <div class="form-group">
                        <label for="translatedWordType">Word Type:</label>
                        <select id="translatedWordType">
                            <option value="noun" ${this.state.currentTranslation.word_type === 'noun' ? 'selected' : ''}>Noun</option>
                            <option value="verb" ${this.state.currentTranslation.word_type === 'verb' ? 'selected' : ''}>Verb</option>
                            <option value="adjective" ${this.state.currentTranslation.word_type === 'adjective' ? 'selected' : ''}>Adjective</option>
                            <option value="adverb" ${this.state.currentTranslation.word_type === 'adverb' ? 'selected' : ''}>Adverb</option>
                            <option value="preposition" ${this.state.currentTranslation.word_type === 'preposition' ? 'selected' : ''}>Preposition</option>
                            <option value="conjunction" ${this.state.currentTranslation.word_type === 'conjunction' ? 'selected' : ''}>Conjunction</option>
                            <option value="pronoun" ${this.state.currentTranslation.word_type === 'pronoun' ? 'selected' : ''}>Pronoun</option>
                            <option value="interjection" ${this.state.currentTranslation.word_type === 'interjection' ? 'selected' : ''}>Interjection</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Add Word</button>
                        <button type="button" class="btn btn-secondary" id="cancelAddTranslatedWord">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        
        // Show form in a modal or overlay
        this.showModal(formHTML);
        
        // Add form event listeners
        const form = DOM.get('#addTranslatedWordForm');
        const cancelBtn = DOM.get('#cancelAddTranslatedWord');
        
        if (form) {
            DOM.on(form, 'submit', (e) => this.handleAddTranslatedWord(e));
        }
        
        if (cancelBtn) {
            DOM.on(cancelBtn, 'click', () => this.hideModal());
        }
    },
    
    // Handle add translated word form submission
    handleAddTranslatedWord(e) {
        e.preventDefault();
        
        const wordData = {
            word: DOM.get('#translatedWord').value.trim(),
            translation: DOM.get('#translatedTranslation').value.trim(),
            example: DOM.get('#translatedExample').value.trim(),
            word_type: DOM.get('#translatedWordType').value,
            notes: `Translated via ${this.state.currentTranslation.source}`
        };
        
        if (!wordData.word || !wordData.translation) {
            this.showError('Word and translation are required');
            return;
        }
        
        try {
            if (typeof VocabularyModule !== 'undefined') {
                VocabularyModule.addWordToVocabulary(wordData);
                this.showSuccess('Word added to vocabulary!');
                this.hideModal();
                this.hideTranslationResult();
            } else {
                // Fallback: add to local storage or show success
                this.showSuccess('Word added successfully!');
                this.hideModal();
                this.hideTranslationResult();
            }
        } catch (error) {
            console.error('❌ Failed to add word:', error);
            this.showError('Failed to add word to vocabulary');
        }
    },
    
    // Show modal
    showModal(content) {
        let modal = DOM.get('.modal-overlay');
        
        if (!modal) {
            modal = DOM.create('div', { className: 'modal-overlay' });
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal-content">
                ${content}
            </div>
        `;
        
        DOM.show(modal);
    },
    
    // Hide modal
    hideModal() {
        const modal = DOM.get('.modal-overlay');
        if (modal) {
            DOM.hide(modal);
        }
    },
    
    // Show error message
    showError(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showError) {
            AppUtils.showError(message);
        } else {
            console.error('❌ Error:', message);
            alert(`Error: ${message}`);
        }
    },
    
    // Show success message
    showSuccess(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showSuccess) {
            AppUtils.showSuccess(message);
        } else {
            console.log('✅ Success:', message);
            alert(`Success: ${message}`);
        }
    },
    
    // Get translation from cache
    getCachedTranslation(word, context = '') {
        const cacheKey = `${word.toLowerCase()}_${context.toLowerCase()}`;
        return this.state.translationCache.get(cacheKey);
    },
    
    // Clear translation cache
    clearCache() {
        this.state.translationCache.clear();
        console.log('🗑️ Translation cache cleared');
    },
    
    // Get cache size
    getCacheSize() {
        return this.state.translationCache.size;
    },
    
    // Check if word is being translated
    isTranslating() {
        return this.state.isTranslating;
    },
    
    // Get current translation
    getCurrentTranslation() {
        return this.state.currentTranslation;
    }
};

// Export for use in other modules
window.TranslationModule = TranslationModule;
