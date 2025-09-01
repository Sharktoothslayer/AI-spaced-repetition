// ========================================
// MAIN JAVASCRIPT - Application Entry Point
// ========================================

// Global state management
window.AppState = {
    currentTab: 'chat',
    currentVocabulary: [],
    newWords: [],
    newWordsIntroduced: new Set(),
    newWordsData: new Map(),
    reviewWords: [],
    currentReviewWord: null
};

// Main initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing AI Language Learning App...');
    
    // Initialize all modules
    initializeTabNavigation();
    initializeChatModule();
    initializeVocabularyModule();
    initializeReviewModule();
    initializeStatsModule();
    
    // Load initial vocabulary
    loadCurrentVocabulary();
    
    console.log('✅ App initialization complete');
});

// Tab Navigation System
function initializeTabNavigation() {
    const navButtons = document.querySelectorAll('.nav-button');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            console.log(`🔄 Switching to tab: ${targetTab}`);
            
            // Update active states
            navButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
            
            // Load content based on tab
            switch(targetTab) {
                case 'chat':
                    if (typeof loadChatContent === 'function') loadChatContent();
                    break;
                case 'vocabulary':
                    if (typeof loadVocabularyContent === 'function') loadVocabularyContent();
                    break;
                case 'review':
                    if (typeof loadReviewContent === 'function') loadReviewContent();
                    break;
                case 'stats':
                    if (typeof loadStatsContent === 'function') loadStatsContent();
                    break;
            }
            
            // Update app state
            AppState.currentTab = targetTab;
        });
    });
}

// Module initialization functions
function initializeChatModule() {
    if (typeof ChatModule !== 'undefined') {
        ChatModule.init();
    }
}

function initializeVocabularyModule() {
    if (typeof VocabularyModule !== 'undefined') {
        VocabularyModule.init();
    }
}

function initializeReviewModule() {
    if (typeof ReviewModule !== 'undefined') {
        ReviewModule.init();
    }
}

function initializeStatsModule() {
    if (typeof StatsModule !== 'undefined') {
        StatsModule.init();
    }
}

// Global utility functions
function showError(message, container = null) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const targetContainer = container || document.querySelector('.main-content');
    targetContainer.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message, container = null) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    
    const targetContainer = container || document.querySelector('.main-content');
    targetContainer.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Global state management functions
function updateAppState(key, value) {
    AppState[key] = value;
    console.log(`📊 App state updated: ${key} =`, value);
}

function getAppState(key) {
    return AppState[key];
}

// Export for use in other modules
window.AppUtils = {
    showError,
    showSuccess,
    updateAppState,
    getAppState
};
