// ========================================
// VOCABULARY MODULE - Vocabulary Management
// ========================================

const VocabularyModule = {
    // Module state
    state: {
        isInitialized: false,
        words: [],
        filteredWords: [],
        searchQuery: '',
        currentWord: null,
        isAddingWord: false
    },
    
    // Initialize the vocabulary module
    init() {
        if (this.state.isInitialized) return;
        
        console.log('📚 Initializing Vocabulary Module...');
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Load initial vocabulary
        this.loadVocabulary();
        
        this.state.isInitialized = true;
        console.log('✅ Vocabulary Module initialized');
    },
    
    // Initialize event listeners
    initializeEventListeners() {
        // Add word button
        const addWordBtn = DOM.get('#addWordBtn');
        if (addWordBtn) {
            DOM.on(addWordBtn, 'click', () => this.showAddWordForm());
        }
        
        // Search input
        const searchInput = DOM.get('#searchInput');
        if (searchInput) {
            DOM.on(searchInput, 'input', (e) => this.handleSearch(e.target.value));
        }
        
        // Global event delegation for word actions
        DOM.on(document, 'click', (e) => this.handleGlobalClick(e));
    },
    
    // Load vocabulary from backend
    async loadVocabulary() {
        try {
            console.log('📚 Loading vocabulary...');
            
            if (typeof API !== 'undefined') {
                const response = await API.get('/api/sr/words');
                if (response.words) {
                    this.state.words = response.words;
                    this.state.filteredWords = [...response.words];
                    this.renderWordsList();
                    console.log(`✅ Loaded ${response.words.length} vocabulary words`);
                }
            } else {
                console.warn('⚠️ API module not available');
                // Use sample data for development
                this.loadSampleData();
            }
        } catch (error) {
            console.error('❌ Failed to load vocabulary:', error);
            this.showError('Failed to load vocabulary');
        }
    },
    
    // Load sample data for development
    loadSampleData() {
        this.state.words = [
            {
                id: 1,
                word: 'ciao',
                translation: 'hello',
                example: 'Ciao! Come stai?',
                word_type: 'interjection',
                notes: 'Informal greeting'
            },
            {
                id: 2,
                word: 'grazie',
                translation: 'thank you',
                example: 'Grazie mille!',
                word_type: 'interjection',
                notes: 'Common expression of gratitude'
            }
        ];
        this.state.filteredWords = [...this.state.words];
        this.renderWordsList();
    },
    
    // Handle search input
    handleSearch(query) {
        this.state.searchQuery = query.toLowerCase();
        
        if (!query.trim()) {
            this.state.filteredWords = [...this.state.words];
        } else {
            this.state.filteredWords = this.state.words.filter(word => 
                word.word.toLowerCase().includes(query) ||
                word.translation.toLowerCase().includes(query) ||
                word.example.toLowerCase().includes(query)
            );
        }
        
        this.renderWordsList();
    },
    
    // Render words list
    renderWordsList() {
        const wordsList = DOM.get('#wordsList');
        if (!wordsList) return;
        
        if (this.state.filteredWords.length === 0) {
            wordsList.innerHTML = `
                <div class="no-words">
                    <h3>No words found</h3>
                    <p>${this.state.searchQuery ? 'Try adjusting your search terms.' : 'Add your first word to get started!'}</p>
                </div>
            `;
            return;
        }
        
        wordsList.innerHTML = this.state.filteredWords.map(word => this.renderWordItem(word)).join('');
    },
    
    // Render individual word item
    renderWordItem(word) {
        return `
            <div class="word-item" data-word-id="${word.id}">
                <div class="word-header">
                    <span class="word-text">${word.word}</span>
                    <button class="delete-word-btn" data-action="delete" data-word-id="${word.id}">
                        Delete
                    </button>
                </div>
                <div class="word-translation">${word.translation}</div>
                <div class="word-type">${word.word_type}</div>
                ${word.example ? `<div class="word-example">${word.example}</div>` : ''}
                ${word.notes ? `<div class="word-notes">${word.notes}</div>` : ''}
                <div class="word-scheduling">
                    <button class="schedule-info-btn" data-action="schedule-info" data-word-id="${word.id}">
                        Show Schedule Info
                    </button>
                </div>
            </div>
        `;
    },
    
    // Handle global click events
    handleGlobalClick(e) {
        const action = e.target.dataset.action;
        const wordId = e.target.dataset.wordId;
        
        if (!action || !wordId) return;
        
        switch (action) {
            case 'delete':
                this.deleteWord(wordId);
                break;
            case 'schedule-info':
                this.showScheduleInfo(wordId);
                break;
        }
    },
    
    // Show add word form
    showAddWordForm() {
        if (this.state.isAddingWord) return;
        
        this.state.isAddingWord = true;
        
        const wordsList = DOM.get('#wordsList');
        if (!wordsList) return;
        
        const formHTML = `
            <div class="add-word-form">
                <h3>Add New Word</h3>
                <form id="addWordForm">
                    <div class="form-group">
                        <label for="newWord">Italian Word:</label>
                        <input type="text" id="newWord" required>
                    </div>
                    <div class="form-group">
                        <label for="newTranslation">Translation:</label>
                        <input type="text" id="newTranslation" required>
                    </div>
                    <div class="form-group">
                        <label for="newExample">Example:</label>
                        <input type="text" id="newExample">
                    </div>
                    <div class="form-group">
                        <label for="newWordType">Word Type:</label>
                        <select id="newWordType">
                            <option value="noun">Noun</option>
                            <option value="verb">Verb</option>
                            <option value="adjective">Adjective</option>
                            <option value="adverb">Adverb</option>
                            <option value="preposition">Preposition</option>
                            <option value="conjunction">Conjunction</option>
                            <option value="pronoun">Pronoun</option>
                            <option value="interjection">Interjection</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="newNotes">Notes:</label>
                        <textarea id="newNotes"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Add Word</button>
                        <button type="button" class="btn btn-secondary" id="cancelAddWord">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        
        wordsList.insertAdjacentHTML('afterbegin', formHTML);
        
        // Add form event listeners
        const form = DOM.get('#addWordForm');
        const cancelBtn = DOM.get('#cancelAddWord');
        
        if (form) {
            DOM.on(form, 'submit', (e) => this.handleAddWord(e));
        }
        
        if (cancelBtn) {
            DOM.on(cancelBtn, 'click', () => this.hideAddWordForm());
        }
    },
    
    // Handle add word form submission
    async handleAddWord(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const wordData = {
            word: DOM.get('#newWord').value.trim(),
            translation: DOM.get('#newTranslation').value.trim(),
            example: DOM.get('#newExample').value.trim(),
            word_type: DOM.get('#newWordType').value,
            notes: DOM.get('#newNotes').value.trim()
        };
        
        if (!wordData.word || !wordData.translation) {
            this.showError('Word and translation are required');
            return;
        }
        
        try {
            if (typeof API !== 'undefined') {
                const response = await API.post('/api/sr/words', wordData);
                if (response.word) {
                    this.state.words.unshift(response.word);
                    this.state.filteredWords = [...this.state.words];
                    this.renderWordsList();
                    this.showSuccess('Word added successfully!');
                    this.hideAddWordForm();
                }
            } else {
                // Add to local state for development
                const newWord = {
                    id: Date.now(),
                    ...wordData,
                    created_at: new Date().toISOString()
                };
                this.state.words.unshift(newWord);
                this.state.filteredWords = [...this.state.words];
                this.renderWordsList();
                this.showSuccess('Word added successfully!');
                this.hideAddWordForm();
            }
        } catch (error) {
            console.error('❌ Failed to add word:', error);
            this.showError('Failed to add word');
        }
    },
    
    // Hide add word form
    hideAddWordForm() {
        this.state.isAddingWord = false;
        const form = DOM.get('.add-word-form');
        if (form) {
            form.remove();
        }
    },
    
    // Delete word
    async deleteWord(wordId) {
        if (!confirm('Are you sure you want to delete this word?')) return;
        
        try {
            if (typeof API !== 'undefined') {
                await API.delete(`/api/sr/words/${wordId}`);
            }
            
            // Remove from local state
            this.state.words = this.state.words.filter(w => w.id != wordId);
            this.state.filteredWords = this.state.filteredWords.filter(w => w.id != wordId);
            this.renderWordsList();
            
            this.showSuccess('Word deleted successfully!');
        } catch (error) {
            console.error('❌ Failed to delete word:', error);
            this.showError('Failed to delete word');
        }
    },
    
    // Show schedule info for word
    showScheduleInfo(wordId) {
        const word = this.state.words.find(w => w.id == wordId);
        if (!word) return;
        
        // This would typically fetch schedule info from the backend
        alert(`Schedule info for "${word.word}":\n\nThis feature will show when the word is due for review.`);
    },
    
    // Show error message
    showError(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showError) {
            AppUtils.showError(message, DOM.get('#wordsList'));
        } else {
            console.error('❌ Error:', message);
        }
    },
    
    // Show success message
    showSuccess(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showSuccess) {
            AppUtils.showSuccess(message, DOM.get('#wordsList'));
        } else {
            console.log('✅ Success:', message);
        }
    },
    
    // Get current vocabulary
    getVocabulary() {
        return this.state.words;
    },
    
    // Get filtered vocabulary
    getFilteredVocabulary() {
        return this.state.filteredWords;
    },
    
    // Check if word exists
    hasWord(word) {
        return this.state.words.some(w => w.word.toLowerCase() === word.toLowerCase());
    },
    
    // Add word to vocabulary (for external use)
    addWordToVocabulary(wordData) {
        const newWord = {
            id: Date.now(),
            ...wordData,
            created_at: new Date().toISOString()
        };
        
        this.state.words.unshift(newWord);
        this.state.filteredWords = [...this.state.words];
        this.renderWordsList();
        
        return newWord;
    }
};

// Export for use in other modules
window.VocabularyModule = VocabularyModule;
