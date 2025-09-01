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
            
            // Safely get and activate the target tab
            const targetTabElement = document.getElementById(`${targetTab}-tab`);
            if (targetTabElement) {
                targetTabElement.classList.add('active');
            } else {
                console.warn(`⚠️ Tab element not found: ${targetTab}-tab`);
                // If the tab doesn't exist, we need to load it dynamically
                loadTabDynamically(targetTab);
            }
            
            // Load content based on tab
            switch(targetTab) {
                case 'chat':
                    loadChatContent();
                    break;
                case 'vocabulary':
                    loadVocabularyContent();
                    break;
                case 'review':
                    loadReviewContent();
                    break;
                case 'stats':
                    loadStatsContent();
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

// Dynamic tab loading
function loadTabDynamically(tabName) {
    console.log(`📥 Loading tab dynamically: ${tabName}`);
    
    // For now, we'll just show a placeholder
    // In a real app, you might fetch the tab content via AJAX
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        // Create a temporary tab content
        const tempTab = document.createElement('div');
        tempTab.id = `${tabName}-tab`;
        tempTab.className = 'tab-content active';
        tempTab.innerHTML = `
            <div class="loading-placeholder">
                <h2>Loading ${tabName}...</h2>
                <p>This tab is being loaded dynamically.</p>
            </div>
        `;
        
        // Remove any existing tab content
        const existingTabs = mainContent.querySelectorAll('.tab-content');
        existingTabs.forEach(tab => tab.remove());
        
        // Add the new tab
        mainContent.appendChild(tempTab);
    }
}

// Load current vocabulary from backend
function loadCurrentVocabulary() {
    console.log('📚 Loading current vocabulary...');
    
    // This would typically make an API call to get vocabulary
    // For now, we'll just log that it's being loaded
    if (typeof API !== 'undefined') {
        API.get('/api/sr/words')
            .then(response => {
                if (response.words) {
                    AppState.currentVocabulary = response.words;
                    console.log(`✅ Loaded ${response.words.length} vocabulary words`);
                }
            })
            .catch(error => {
                console.warn('⚠️ Could not load vocabulary:', error);
                AppState.currentVocabulary = [];
            });
    } else {
        console.warn('⚠️ API module not loaded yet');
        AppState.currentVocabulary = [];
    }
}

// Tab content loading functions
function loadChatContent() {
    console.log('💬 Loading chat content...');
    // Chat content is already loaded as default
}

function loadVocabularyContent() {
    console.log('📚 Loading vocabulary content...');
    // This would load vocabulary-specific content
    // For now, just log the action
}

function loadReviewContent() {
    console.log('🔄 Loading review content...');
    // This would load review-specific content
    // For now, just log the action
}

function loadStatsContent() {
    console.log('📊 Loading stats content...');
    // This would load stats-specific content
    // For now, just log the action
}

// Export for use in other modules
window.AppUtils = {
    showError,
    showSuccess,
    updateAppState,
    getAppState
};
