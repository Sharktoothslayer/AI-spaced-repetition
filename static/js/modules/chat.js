// ========================================
// CHAT MODULE - Chat Functionality
// ========================================

const ChatModule = {
    // Module state
    state: {
        isInitialized: false,
        messageInput: null,
        sendButton: null,
        chatMessages: null,
        vocabularyToggle: null,
        addNewWordsBtn: null,
        endConversationBtn: null
    },
    
    // Initialize the chat module
    init() {
        if (this.state.isInitialized) return;
        
        console.log('💬 Initializing Chat Module...');
        
        // Get DOM elements
        this.state.messageInput = document.getElementById('messageInput');
        this.state.sendButton = document.getElementById('sendButton');
        this.state.chatMessages = document.getElementById('chatMessages');
        this.state.vocabularyToggle = document.getElementById('vocabularyToggle');
        this.state.addNewWordsBtn = document.getElementById('addNewWordsBtn');
        this.state.endConversationBtn = document.getElementById('endConversationBtn');
        
        // Check if elements exist
        if (!this.validateElements()) {
            console.error('❌ Required chat elements not found');
            return;
        }
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set initial toggle label
        this.updateToggleLabel();
        
        this.state.isInitialized = true;
        console.log('✅ Chat Module initialized');
    },
    
    // Validate required DOM elements
    validateElements() {
        const required = [
            'messageInput',
            'sendButton', 
            'chatMessages'
        ];
        
        return required.every(key => this.state[key] !== null);
    },
    
    // Set up event listeners
    setupEventListeners() {
        // Send button click
        this.state.sendButton.addEventListener('click', () => {
            this.handleSendMessage();
        });
        
        // Enter key press
        this.state.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        // Vocabulary toggle change
        if (this.state.vocabularyToggle) {
            this.state.vocabularyToggle.addEventListener('change', () => {
                this.handleToggleChange();
            });
        }
        
        // End conversation button
        if (this.state.endConversationBtn) {
            this.state.endConversationBtn.addEventListener('click', () => {
                this.handleEndConversation();
            });
        }
        
        // Add new words button
        if (this.state.addNewWordsBtn) {
            this.state.addNewWordsBtn.addEventListener('click', () => {
                this.handleAddNewWords();
            });
        }
    },
    
    // Handle sending a message
    async handleSendMessage() {
        const message = this.state.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, true);
        this.state.messageInput.value = '';
        
        // Send message to AI
        await this.sendMessage(message);
    },
    
    // Add message to chat
    addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = isUser ? 'You' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Handle HTML content for AI responses (to show highlighted new words)
        if (isUser) {
            messageContent.textContent = content;
        } else {
            messageContent.innerHTML = content;
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.state.chatMessages.appendChild(messageDiv);
        this.state.chatMessages.scrollTop = this.state.chatMessages.scrollHeight;
    },
    
    // Send message to AI
    async sendMessage(message) {
        try {
            this.state.sendButton.disabled = true;
            this.state.sendButton.textContent = 'Sending...';
            
            // Show loading indicator
            this.showLoadingIndicator();
            
            // Get current vocabulary state
            const isStrictMode = this.state.vocabularyToggle?.checked || false;
            const currentVocabulary = AppState.currentVocabulary || [];
            
            console.log('📤 Sending message with settings:', {
                strictMode: isStrictMode,
                vocabularySize: currentVocabulary.length,
                message: message
            });
            
            // Send message via API
            const response = await API.chat.sendMessage(message, isStrictMode, currentVocabulary);
            
            console.log('📥 AI Response received:', response.response);
            
            // Hide loading indicator
            this.hideLoadingIndicator();
            
            // Process AI response to highlight new words
            const processedResponse = this.processAIResponse(response.response);
            this.addMessage(processedResponse, false);
            
            // Show end conversation button if new words were introduced
            if (AppState.newWordsIntroduced.size > 0) {
                this.showEndConversationButton();
            }
            
        } catch (error) {
            this.hideLoadingIndicator();
            AppUtils.showError(error.message || 'Failed to get response from AI');
            console.error('Error sending message:', error);
        } finally {
            this.state.sendButton.disabled = false;
            this.state.sendButton.textContent = 'Send';
        }
    },
    
    // Show loading indicator
    showLoadingIndicator() {
        const aiThinking = document.getElementById('aiThinking');
        if (aiThinking) {
            aiThinking.style.display = 'flex';
        }
    },
    
    // Hide loading indicator
    hideLoadingIndicator() {
        const aiThinking = document.getElementById('aiThinking');
        if (aiThinking) {
            aiThinking.style.display = 'none';
        }
    },
    
    // Process AI response and highlight new words
    processAIResponse(response) {
        // Filter out ATTENZIONE warning messages
        if (response.includes('⚠️ ATTENZIONE:')) {
            const startIndex = response.indexOf('Ecco la mia risposta:');
            if (startIndex !== -1) {
                response = response.substring(startIndex + 'Ecco la mia risposta:'.length).trim();
            }
        }
        
        // Enhanced patterns to catch all Italian words
        const patterns = [
            '\\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\\w*\\b',
            '\\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\\b',
            '\\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\'[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\\w*\\b',
            '\\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz][aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\\b',
            '\\b[àèéìòù]\\b',
            '\\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]{1,2}\\b',
            '\\b\\w*[àèéìòù]\\b',
            '\\b[àèéìòù]\\w*\\b',
            '\\b\\w*[àèéìòù]\\w*\\b'
        ];
        
        let processedResponse = response;
        const newWordsFound = [];
        
        // Process each pattern
        patterns.forEach((pattern, index) => {
            const regex = new RegExp(pattern, 'gi');
            const matches = processedResponse.match(regex);
            
            if (matches) {
                matches.forEach(match => {
                    const lowerMatch = match.toLowerCase();
                    
                    // Check if this word is not in current vocabulary
                    if (!AppState.currentVocabulary.some(vocabWord => 
                        vocabWord.toLowerCase() === lowerMatch
                    )) {
                        // Check if we haven't already found this word
                        if (!newWordsFound.some(w => w.word.toLowerCase() === lowerMatch)) {
                            console.log(`✨ New word detected: "${match}"`);
                            newWordsFound.push({
                                word: match,
                                original: match,
                                translation: null
                            });
                            
                            // Add to newWords array for later processing
                            if (!AppState.newWords.some(w => w.word.toLowerCase() === lowerMatch)) {
                                AppState.newWords.push({
                                    word: match,
                                    original: match,
                                    translation: null
                                });
                            }
                        }
                    }
                });
            }
        });
        
        console.log(`🎯 Total new words found: ${newWordsFound.length}`, newWordsFound.map(w => w.word));
        
        // Highlight new words in the response
        newWordsFound.forEach(wordObj => {
            const regex = new RegExp(`\\b${wordObj.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
            processedResponse = processedResponse.replace(regex, 
                `<span class="new-word" data-word="${wordObj.word}" style="color: red; font-weight: bold;">${wordObj.word}</span>`
            );
        });
        
        // Show "Add New Words" button if new words were found
        if (newWordsFound.length > 0) {
            this.showAddNewWordsButton(newWordsFound.length);
        }
        
        return processedResponse;
    },
    
    // Show add new words button
    showAddNewWordsButton(count) {
        if (this.state.addNewWordsBtn) {
            this.state.addNewWordsBtn.style.display = 'inline-block';
            document.getElementById('newWordCount').textContent = `(${count})`;
        }
    },
    
    // Show end conversation button
    showEndConversationButton() {
        if (this.state.endConversationBtn) {
            this.state.endConversationBtn.style.display = 'block';
        }
    },
    
    // Handle toggle change
    handleToggleChange() {
        // Reset conversation when changing modes
        this.resetConversation();
        
        // Update toggle label to show current mode
        this.updateToggleLabel();
        
        // Log current vocabulary for debugging
        console.log('Current vocabulary for AI:', AppState.currentVocabulary);
    },
    
    // Update toggle label
    updateToggleLabel() {
        const toggleLabel = document.querySelector('.toggle-text');
        if (toggleLabel && this.state.vocabularyToggle) {
            const isStrictMode = this.state.vocabularyToggle.checked;
            if (isStrictMode) {
                toggleLabel.textContent = 'Strict Mode: ON';
                toggleLabel.style.color = '#28a745';
                console.log('🟢 STRICT MODE ENABLED - AI should use ONLY vocabulary words');
            } else {
                toggleLabel.textContent = 'Learning Mode: ON (1-5 new words)';
                toggleLabel.style.color = '#ffc107';
                console.log('🟡 LEARNING MODE ENABLED - AI can introduce 1-5 new words');
            }
        }
    },
    
    // Reset conversation state
    resetConversation() {
        AppState.newWordsIntroduced.clear();
        AppState.newWordsData.clear();
        AppState.newWords = [];
        
        if (this.state.endConversationBtn) {
            this.state.endConversationBtn.style.display = 'none';
        }
        
        if (this.state.addNewWordsBtn) {
            this.state.addNewWordsBtn.style.display = 'none';
        }
        
        // Clear chat messages except the initial greeting
        const initialMessage = this.state.chatMessages.querySelector('.message.ai');
        this.state.chatMessages.innerHTML = '';
        if (initialMessage) {
            this.state.chatMessages.appendChild(initialMessage);
        }
    },
    
    // Handle end conversation
    handleEndConversation() {
        if (AppState.newWordsIntroduced.size === 0) {
            alert('No new words to add!');
            return;
        }
        
        const confirmed = confirm(`Add ${AppState.newWordsIntroduced.size} new words to your vocabulary?`);
        if (!confirmed) return;
        
        // This will be handled by the vocabulary module
        if (typeof VocabularyModule !== 'undefined') {
            VocabularyModule.addNewWordsFromChat();
        }
    },
    
    // Handle add new words
    handleAddNewWords() {
        if (AppState.newWords.length === 0) {
            alert('No new words to add!');
            return;
        }
        
        // This will be handled by the vocabulary module
        if (typeof VocabularyModule !== 'undefined') {
            VocabularyModule.addNewWordsFromChat();
        }
    }
};

// Export for use in other modules
window.ChatModule = ChatModule;
