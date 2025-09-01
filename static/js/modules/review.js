// ========================================
// REVIEW MODULE - Spaced Repetition Reviews
// ========================================

const ReviewModule = {
    // Module state
    state: {
        isInitialized: false,
        dueWords: [],
        currentWord: null,
        isShowingAnswer: false,
        reviewStats: {
            total: 0,
            due: 0,
            overdue: 0,
            completed: 0
        }
    },
    
    // Initialize the review module
    init() {
        if (this.state.isInitialized) return;
        
        console.log('🔄 Initializing Review Module...');
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Load review data
        this.loadReviewData();
        
        this.state.isInitialized = true;
        console.log('✅ Review Module initialized');
    },
    
    // Initialize event listeners
    initializeEventListeners() {
        // Global event delegation for review actions
        DOM.on(document, 'click', (e) => this.handleGlobalClick(e));
    },
    
    // Load review data from backend
    async loadReviewData() {
        try {
            console.log('🔄 Loading review data...');
            
            if (typeof API !== 'undefined') {
                // Load due words
                const dueResponse = await API.get('/api/sr/due');
                if (dueResponse.words) {
                    this.state.dueWords = dueResponse.words;
                }
                
                // Load overdue words
                const overdueResponse = await API.get('/api/sr/overdue');
                if (overdueResponse.words) {
                    this.state.dueWords = [...this.state.dueWords, ...overdueResponse.words];
                }
                
                // Load stats
                const statsResponse = await API.get('/api/sr/stats');
                if (statsResponse) {
                    this.state.reviewStats = {
                        total: statsResponse.total_words || 0,
                        due: statsResponse.due_count || 0,
                        overdue: statsResponse.overdue_count || 0,
                        completed: statsResponse.completed_reviews || 0
                    };
                }
            } else {
                console.warn('⚠️ API module not available');
                // Use sample data for development
                this.loadSampleData();
            }
            
            this.updateReviewDisplay();
            this.renderReviewCard();
            
        } catch (error) {
            console.error('❌ Failed to load review data:', error);
            this.showError('Failed to load review data');
        }
    },
    
    // Load sample data for development
    loadSampleData() {
        this.state.dueWords = [
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
        
        this.state.reviewStats = {
            total: 2,
            due: 2,
            overdue: 0,
            completed: 0
        };
    },
    
    // Update review display
    updateReviewDisplay() {
        // Update due count
        const dueCount = DOM.get('#dueCount');
        if (dueCount) {
            dueCount.textContent = this.state.dueWords.length;
        }
        
        // Update total words count
        const totalWords = DOM.get('#totalWords');
        if (totalWords) {
            totalWords.textContent = this.state.reviewStats.total;
        }
        
        // Update due words count
        const dueWords = DOM.get('#dueWords');
        if (dueWords) {
            dueWords.textContent = this.state.reviewStats.due;
        }
        
        // Update overdue words count
        const overdueWords = DOM.get('#overdueWords');
        if (overdueWords) {
            overdueWords.textContent = this.state.reviewStats.overdue;
        }
    },
    
    // Render review card
    renderReviewCard() {
        const reviewCard = DOM.get('.review-card');
        if (!reviewCard) return;
        
        if (this.state.dueWords.length === 0) {
            this.renderNoReviews();
            return;
        }
        
        // Get next word to review
        this.state.currentWord = this.state.dueWords[0];
        
        if (this.state.isShowingAnswer) {
            this.renderAnswerCard();
        } else {
            this.renderQuestionCard();
        }
    },
    
    // Render question card (front of card)
    renderQuestionCard() {
        const reviewCard = DOM.get('.review-card');
        if (!reviewCard || !this.state.currentWord) return;
        
        reviewCard.innerHTML = `
            <div class="card-content">
                <div class="word-display">
                    <h2>${this.state.currentWord.word}</h2>
                    <div class="word-type-badge">${this.state.currentWord.word_type}</div>
                </div>
                <button class="show-answer-btn" data-action="show-answer">
                    <span class="btn-icon">👁️</span>
                    <span class="btn-text">Show Answer</span>
                </button>
            </div>
        `;
    },
    
    // Render answer card (back of card)
    renderAnswerCard() {
        const reviewCard = DOM.get('.review-card');
        if (!reviewCard || !this.state.currentWord) return;
        
        reviewCard.innerHTML = `
            <div class="card-content">
                <div class="word-display">
                    <h2>${this.state.currentWord.word}</h2>
                    <div class="word-type-badge">${this.state.currentWord.word_type}</div>
                </div>
                
                <div class="answer-section">
                    <div class="translation-section">
                        <h3>Translation</h3>
                        <p>${this.state.currentWord.translation}</p>
                    </div>
                    
                    ${this.state.currentWord.example ? `
                        <div class="example-section">
                            <h4>Example</h4>
                            <p>${this.state.currentWord.example}</p>
                        </div>
                    ` : ''}
                    
                    <div class="quality-buttons">
                        <button class="quality-btn again" data-action="rate-quality" data-quality="0">
                            <span class="btn-label">Again</span>
                            <span class="btn-preview">Review again soon</span>
                        </button>
                        <button class="quality-btn hard" data-action="rate-quality" data-quality="1">
                            <span class="btn-label">Hard</span>
                            <span class="btn-preview">Review in a few days</span>
                        </button>
                        <button class="quality-btn good" data-action="rate-quality" data-quality="2">
                            <span class="btn-label">Good</span>
                            <span class="btn-preview">Review in a week</span>
                        </button>
                        <button class="quality-btn easy" data-action="rate-quality" data-quality="3">
                            <span class="btn-label">Easy</span>
                            <span class="btn-preview">Review in a month</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Render no reviews state
    renderNoReviews() {
        const reviewCard = DOM.get('.review-card');
        if (!reviewCard) return;
        
        reviewCard.innerHTML = `
            <div class="no-reviews">
                <div class="no-reviews-content">
                    <div class="no-reviews-icon">🎉</div>
                    <h3>No Reviews Due!</h3>
                    <p>Great job! You're all caught up with your reviews.</p>
                    <p class="subtitle">Check back later for new words to review.</p>
                </div>
            </div>
        `;
    },
    
    // Handle global click events
    handleGlobalClick(e) {
        const action = e.target.dataset.action;
        
        if (!action) return;
        
        switch (action) {
            case 'show-answer':
                this.showAnswer();
                break;
            case 'rate-quality':
                const quality = parseInt(e.target.dataset.quality);
                this.rateQuality(quality);
                break;
        }
    },
    
    // Show answer for current word
    showAnswer() {
        this.state.isShowingAnswer = true;
        this.renderReviewCard();
    },
    
    // Rate quality of review
    async rateQuality(quality) {
        if (!this.state.currentWord) return;
        
        try {
            console.log(`🔄 Rating word "${this.state.currentWord.word}" with quality: ${quality}`);
            
            if (typeof API !== 'undefined') {
                // Send rating to backend
                await API.post('/api/sr/review', {
                    word_id: this.state.currentWord.id,
                    quality: quality
                });
            }
            
            // Remove word from due list
            this.state.dueWords = this.state.dueWords.filter(w => w.id !== this.state.currentWord.id);
            
            // Update stats
            this.state.reviewStats.completed++;
            this.state.reviewStats.due = Math.max(0, this.state.reviewStats.due - 1);
            
            // Show success message
            this.showSuccess(`Word reviewed! Quality: ${this.getQualityLabel(quality)}`);
            
            // Reset state and show next word
            this.state.currentWord = null;
            this.state.isShowingAnswer = false;
            
            // Update display
            this.updateReviewDisplay();
            this.renderReviewCard();
            
        } catch (error) {
            console.error('❌ Failed to submit review:', error);
            this.showError('Failed to submit review');
        }
    },
    
    // Get quality label
    getQualityLabel(quality) {
        const labels = ['Again', 'Hard', 'Good', 'Easy'];
        return labels[quality] || 'Unknown';
    },
    
    // Show error message
    showError(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showError) {
            AppUtils.showError(message, DOM.get('.review-card'));
        } else {
            console.error('❌ Error:', message);
        }
    },
    
    // Show success message
    showSuccess(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showSuccess) {
            AppUtils.showSuccess(message, DOM.get('.review-card'));
        } else {
            console.log('✅ Success:', message);
        }
    },
    
    // Get current review stats
    getReviewStats() {
        return this.state.reviewStats;
    },
    
    // Get due words count
    getDueWordsCount() {
        return this.state.dueWords.length;
    },
    
    // Check if there are words to review
    hasWordsToReview() {
        return this.state.dueWords.length > 0;
    },
    
    // Get next word to review
    getNextWord() {
        return this.state.dueWords[0] || null;
    },
    
    // Refresh review data
    async refreshReviewData() {
        await this.loadReviewData();
    }
};

// Export for use in other modules
window.ReviewModule = ReviewModule;
