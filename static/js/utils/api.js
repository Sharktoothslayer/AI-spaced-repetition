// ========================================
// API UTILITY MODULE - Backend Communication
// ========================================

const API = {
    // Base configuration
    baseURL: '',
    timeout: 30000,
    
    // HTTP methods
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: this.timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`❌ API GET error for ${endpoint}:`, error);
            throw error;
        }
    },
    
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                timeout: this.timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`❌ API POST error for ${endpoint}:`, error);
            throw error;
        }
    },
    
    async delete(endpoint) {
        try {
            const response = await fetch(endpoint, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: this.timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`❌ API DELETE error for ${endpoint}:`, error);
            throw error;
        }
    },
    
    // Chat API endpoints
    chat: {
        async sendMessage(message, strictMode = false, currentVocabulary = []) {
            return await API.post('/api/chat', {
                message,
                strict_mode: strictMode,
                current_vocabulary: currentVocabulary
            });
        },
        
        async resetChat(sessionId = 'default') {
            return await API.post('/api/chat/reset', { session_id: sessionId });
        }
    },
    
    // Spaced Repetition API endpoints
    spacedRepetition: {
        async getWords() {
            return await API.get('/api/sr/words');
        },
        
        async addWord(wordData) {
            return await API.post('/api/sr/words', wordData);
        },
        
        async deleteWord(wordId) {
            return await API.delete(`/api/sr/words/${wordId}`);
        },
        
        async getDueWords() {
            return await API.get('/api/sr/due');
        },
        
        async getOverdueWords() {
            return await API.get('/api/sr/overdue');
        },
        
        async reviewWord(wordId, quality) {
            return await API.post('/api/sr/review', { word_id: wordId, quality });
        },
        
        async getStats() {
            return await API.get('/api/sr/stats');
        },
        
        async getUpcomingReviews(days = 7) {
            return await API.get('/api/sr/upcoming', { days });
        },
        
        async getDailyUpcomingCounts(days = 7) {
            return await API.get('/api/sr/daily-upcoming', { days });
        },
        
        async getNextReviewInfo(wordId) {
            return await API.get(`/api/sr/words/${wordId}/next-review`);
        },
        
        async getReviewPreview(wordId) {
            return await API.get(`/api/sr/words/${wordId}/review-preview`);
        },
        
        async searchWords(query) {
            return await API.get('/api/sr/search', { q: query });
        }
    },
    
    // Translation API endpoints
    translation: {
        async getAITranslation(word, context = '') {
            return await API.post('/api/sr/ai-translate-word', { word, context });
        },
        
        async getTranslation(word, context = '') {
            return await API.post('/api/sr/ai-translate', { word, context });
        }
    },
    
    // Test endpoint
    async test() {
        return await API.get('/api/test');
    }
};

// Export for use in other modules
window.API = API;
